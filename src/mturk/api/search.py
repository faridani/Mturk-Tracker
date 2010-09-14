# -*- coding: utf-8 -*- 

from mturk.api.utils import elipsis

from wapi.decorators import required_parameter, private
from wapi.parameters import FunctionParameterSet, FunctionParameter
from wapi.responses import SerializableResponse
from wapi.validators import ChoiceValidator

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.utils import simplejson
from django.utils.text import truncate_words, capfirst

from pythonsolr.pysolr import Solr

from cgi import escape

import logging
import re
import urllib2

logger = logging.getLogger('backoffice.api')

ORDER_PARAM_SET = FunctionParameterSet(
    FunctionParameter('sort', str, 'Sort field', default='dt_indexing', validators=ChoiceValidator(choices=[('time','Time')])),
    FunctionParameter('order', str, 'Sorting order', default='asc', validators=ChoiceValidator(choices=[('asc','Ascending'),('desc','Descending')])),
)

ROWS_PARAM_SET = FunctionParameterSet(
    FunctionParameter('start', int, 'Starting record', default=0 ),
    FunctionParameter('rows', int, 'Rows on page', default=10 ),
)
    

class SearchApi(object):


    @private
    def get_facets(self, results):
        
        facets = {}
        for field in results.facets['facet_fields']:
            
            facets[field] = {}
            key = None 
            for i,el in enumerate(results.facets['facet_fields'][field]):
                if i % 2 == 0: 
                    key = el.replace("_"," ")
                else:
                    if field == 'tags':
                        if re.match("^\d+$", key) is None and key.strip() != '' and len(key) >= 4: 
                            facets[field][key] = el
                    elif field == 'location':
                        key = ' '.join((capfirst(s) for s in key.split(' ')))
                        key = '-'.join((capfirst(s) for s in key.split('-')))
                        facets[field][key] = el
                    elif field == 'category' and key == 'blog':
                        continue
                    else:
                        facets[field][key] = el
                    key = None
                    
        return facets
    
    @private
    def get_common_search_params(self,dct):
    
        def prepare_locations_for_solr(params):
            
            boolean_opts    = re.compile("(\sor\s|\sand\s)", re.IGNORECASE)
            whitespace      = re.compile("\s+")
            
            params = ' '.join((re.sub(whitespace, '_',s.strip()) for s in re.split(boolean_opts, params)))
            
            return params
        
        def prepare_params_for_solr(params):
            dissallowed_characters = re.compile("[\-_\(\)\^\"']+", re.IGNORECASE | re.UNICODE)
            dissallowed_characters_beginning = re.compile("[^\w\d\s\-_\(\)\^\"']+", re.IGNORECASE | re.UNICODE)
            params = re.sub(dissallowed_characters, " ", params)
            params = re.sub(dissallowed_characters_beginning, " ", params)
            
            return params 
    
        for k,v in dct.iteritems(): 
            if v == '': del dct[k]
            
        use_highlighting = 'q' in dct and dct['q'].strip() != ''

        query = []
        cities = [] 
               
        if 'q' in dct:
            dct['q'] = prepare_params_for_solr(dct['q'])
            
            if ' ' in dct['q'] or '\t' in dct['q']: 
                query = [unicode('search_field:("%s"~20)^500 OR search_field:(%s)^20' % (dct['q'], dct['q']))]
            else:
                query = [unicode('search_field:(%s)' % (dct['q']))]
                
        fq = []

        params = {
                  'fl': ' '.join([
                         'group_id', 
                         'requester_name', 
                         'requester_id',
                         'content',
                         'description',
                         'title',
                         'keywords',
                         'qualifications',
                         'occurrence_date',
                         'reward'
                         ]),
                  'facet':'on', 
                  'facet.field':['requester_name'],
                  'facet.mincount':1,
                  'facet.limit':20,
                  'hl':'on' if use_highlighting else 'off',
                  'hl.fl': 'content',
                  'hl.simple.pre': '<strong>',
                  'hl.simple.post': '</strong>',
                  'start': dct['start'] if 'start' in dct else 0,
                  'rows': dct['rows'] if 'rows' in dct else 10,
                  'hl.fragsize': 300                
                  }
                
        """
        Setting up all filter query params
        """        
        group_id        = dct['group_id'] if 'group_id' in dct else None
        requester_id    = dct['requester_id'] if 'requester_id' in dct else None
        requester_name  = dct['requester_name'] if 'requester_name' in dct else None
        content         = dct['content'] if 'content' in dct else None
        description     = dct['description'] if 'description' in dct else None
        title           = dct['title'] if 'title' in dct else None
        keywords        = dct['keywords'] if 'keywords' in dct else None
        qualifications  = dct['qualifications'] if 'qualifications' in dct else None
        occurrence_date = dct['occurrence_date'] if 'occurrence_date' in dct else None

        if group_id:        fq.append('group_id:(%s)' % prepare_params_for_solr(group_id))
        if requester_id:    fq.append('requester_id:(%s)' % prepare_params_for_solr(requester_id))
        if requester_name:  fq.append('requester_name:(%s)' % prepare_params_for_solr(requester_name))
        if content:         fq.append('content:(%s)' % prepare_params_for_solr(content))
        if description:     fq.append('description:(%s)' % prepare_params_for_solr(description))        
        if title:           fq.append('title:(%s)' % prepare_params_for_solr(title))     
        if keywords:        fq.append('keywords:(%s)' % prepare_params_for_solr(keywords))     
        if qualifications:  fq.append('qualifications:(%s)' % prepare_params_for_solr(qualifications))     
        if occurrence_date: fq.append('occurrence_date:(%s)' % prepare_params_for_solr(occurrence_date))
        
        """
        If no query is given we use filter query as main query
        """
        if query is None and len(fq)>0:
            query = fq
            fq = []
            
        # sorting
        if 'sort' in dct:
            params['sort']  = "%s %s" % ( dct['sort'], dct['order'] )

        
        if len(query) > 0 and 'sort' not in dct:
            query[0] = '{!boost b=recip(ms(NOW,%s),3.16e-9,1,1)}' % 'occurrence_date' + query[0]
            
        params['fq'] = fq
        
        return query, params, use_highlighting

    @private
    def serialize_search_results(self, results, params, use_highlighting, query):


        def sanitize(results, highlights, use_highlighting):
            
            for r in results:

                ret = {}
                ret['rank']             = 0
                ret['content']          = r['content'] if 'content' in r else ''                
                ret['title']            = elipsis(r['title'] if 'title' in r else '', 150)                    
                ret['description']      = elipsis(r['description'] if 'description' in r else '', 300)      
                
                ret['requester_id']     = r['requester_id'] if 'requester_id' in r else ''
                ret['requester_name']   = r['requester_name'] if 'requester_name' in r else ''
                ret['keywords']         = r['keywords'] if 'keywords' in r else ''
                ret['qualifications']   = r['qualifications'] if 'qualifications' in r else ''
                ret['occurrence_date']  = r['occurrence_date'] if 'occurrence_date' in r else ''
                ret['requester_id']     = r['requester_id'] if 'requester_id' in r else ''
                ret['group_id']         = r['group_id'] if 'group_id' in r else ''     
                ret['reward']           = r['reward'] if 'reward' in r else ''     

                if use_highlighting:                 
                    highlighting = highlights[r['group_id']]['content'][-1] if 'content' in highlights[r['group_id']] else None
                    if highlighting: ret['snippet'] = highlighting
        
                yield ret
    
        objects = list(sanitize(results,results.highlighting,use_highlighting))
        facets = self.get_facets(results)
        results_count = len(objects) if results.hits <= 10 else results.hits
        
        return SerializableResponse([{
            'results_count':results_count,
            'offset':params['start'],
            'results_per_page':params['rows'],
            'results': objects,
            'facets': facets,
        }])


    def search(self,request,dct):

        if 'q' not in dct:
			return SerializableResponse([{
            	'results_count': 0,
            	'offset': 0,
            	'results_per_page': 10,
            	'results': list()
        	}])

        original_query          = dct['q']
        query_transformations   = []

        query_transformations.append(original_query)
        
        if "'" in original_query or '"' in original_query:
            query_transformations.append(re.sub("[\"']*", '', original_query))
      
        solr = Solr(settings.SOLR_MAIN)

        for tq in query_transformations:
            dct['q'] = tq
            q, params, use_highlighting = self.get_common_search_params(dct)
            results = self.serialize_search_results(solr.search(q, **params), params, use_highlighting, dct['q'] if 'q' in dct else '')
            if results.objs[0]['results_count'] != 0:
                return results
        
        return results  
    
    def reindex_hits(self,request,dct):

        main = settings.SOLR_MAIN
        solr = Solr(main)
        urllib2.urlopen(main + "/import_db_hits/?command=full-import&clean=false")
        
        if settings.CACHE_BACKEND.startswith('memcached'):
            cache._cache.flush_all()
        
        return SerializableResponse( [] )

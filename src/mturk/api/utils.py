import re

def cleanup_solr_text(s, dict, html_markup=True):
    
    def resolve_dict(d):
        try:
            '''
            getting i from strin like:
            "5: " 
            '''
            i = int(d.group(0)[:-2])
            if html_markup: 
                ret = '<span class="label">' + dict[i].capitalize().strip() + ': '
            else:
                ret = dict[i].capitalize().strip() + ': '
            return ret.encode('utf-8')
        except:
            return ''             
    
    return re.sub(r'[0-9]+:\s',resolve_dict,s)

def elipsis(s,max_length):
    
    if s is None: return ''
    
    if len(s) > max_length:
        return s[:max_length] + "..."
    else:
        return s

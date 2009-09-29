def get_allhit_url(page=1):
    return 'https://www.mturk.com/mturk/viewhits?selectedSearchType=hitgroups&sortType=LastUpdatedTime%3A1&&searchSpec=HITGroupSearch%23T%232%2310%23-1%23T%23!%23!LastUpdatedTime!1!%23!&pageNumber='+str(page)

def get_group_url(id):
   return "https://www.mturk.com/mturk/preview?groupId=%s" % id
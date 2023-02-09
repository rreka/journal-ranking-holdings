import pandas as pd
import requests
import xml.etree.ElementTree as ElementTree
import re
import config


def getText(elem):
    ''' 
    Get the text from the XML response and return a string.
    '''
    try:
        msg = elem.text  
        msg = msg.replace('<br>', '')
    except:
        msg = ""

    if msg is None:
        msg = "not available"

    return msg


def searchOpenURL(row):
    '''(pandas.DataFrame) --> pandas.Series
    
    This function takes a row of a pandas DataFrame and gets the ISSN of a journal. When used with the pandas apply function, this function uses the ISSNs to run a HTTP query against a library OpenURL link resolver server, retrieves the XML response, and parses out the package name and coverage dates. Using getText, this function returns two columns in a panda Series for each row: a statement of availability, and a statement of coverage (package names and the dates they cover).
    
    '''
    # Create and run an HTTP request against the open URL link resolver 
    #r = requests.get('https://ca01.alma.exlibrisgroup.com/view/uresolver/01UTON_UW/openurl?svc_dat=CTO&issn={}'.format(row['q_issn']))
    r = requests.get('{}svc_dat=CTO&issn={}'.format(config.base_URL, row['q_issn']))
    # Parse the XML response and store it as root
    root = ElementTree.fromstring(r.content)
    # Create a dict of namespace values for use later on, so that the queries of the stored XML response can be cleaner
    ns = {'resolver': 'http://com/exlibris/urm/uresolver/xmlbeans/u'}
    # Create an empty dict that will be used to store the coverage statements for each journal. Key will be the package name, value will be the coverage dates.
    coverage_statement = {}
    
    # get all full-text services
    
    # if there is a full-text service
    if root.findall('.//resolver:context_service[@service_type="getFullTxt"]',ns) != []:
        # set the availability statement to show that there is a full-text
        avail_statement = 'Full-text available'
        print('Full-text available for ' + row['q_issn'])
        # for each full-text service
        for service in root.findall('.//resolver:context_service[@service_type="getFullTxt"]',ns):
            # Create empty str variables to store the details of the full-text service
            servicePackageName = ''
            serviceCoverage = ''
            # get package name of the full-text service and add it to the temporary str variable
            package = service.find('.//resolver:key[@id="package_public_name"]',ns)
            servicePackageName = getText(package)
            
            # get coverage date statement of the full-text service and add it to the temptorary str variable
            avail = service.find('.//resolver:key[@id="Availability"]',ns)
            serviceCoverage = getText(avail)
            # Add the details of this full-text service to the dict
            coverage_statement[servicePackageName] = serviceCoverage
    # When there is no full-text service
    else:
        # set the availability statement to show that there is no full-text
        avail_statement = 'No full-text available'
        print('Full-text not available for ' + row['q_issn'])
    # Return the availability and coverage statements as a pandas Series
    return pd.Series([avail_statement, coverage_statement])


def coverageStatement_availParser(row):
    '''
    (pd.Series) -> pd.Series
    
    This function parses out info from the coverage statements for all packages, and updates the availability statements for the journals to reflect those journals that don't have full-text coverage, those that do up to the present, those with embargo and those with full-text access, but not to the present.
    
    '''
    # Create an empy str for the coverage statement value
    avail_statement = ''
    # Only do run this function if there are full-text resources
    if row['coverage'] != {}:
        # Create an empty variable that will change if the function should stop
        stop = 0
        
        # Check all coverage statements in the dict, and if any ONE of them doesn't contain the words 'most recent' or 'until' (i.e., its up to the current), set the availability statement to available to present and stop.
        for value in row['coverage'].values():
            # Skip values that don't contain any data
            if value != '':
                if not any(s in value for s in ('Most recent', 'until')):
                    avail_statement = 'Full-text available to present'
                    stop = 1
                    break
                    
        # If there was no coverage statement where there was full-text to the present, continue
        if stop == 0:
            for value in row['coverage'].values():
                if value != '':
                    # If there is any ONE line coverage statement that is for an embargo
                    if 'Most recent' in value:
                        avail_statement = 'Full-text available with embargo'
                        stop = 1
                        break
                        
        # If there is no statement up to the present, nor for an embargo, then it must be available, but not complete.
        if stop == 0:
            for value in row['coverage'].values():
                if value != '':
                    if 'until' in value:
                        avail_statement = 'Full-text available, but not complete'
    else:
        avail_statement = 'No full-text available'
    return pd.Series([avail_statement])


def coverageStatement_yearsParser(row):
    '''
    (pd.Series) -> pd.Series
    
    This function takes the coverage statements provided by the link resolver, parses out the dates, and creates a one line date range of coverage.
    '''
    
    tempList = []
    # Don't do this if there are no coverage statements
    if row['coverage'] != {}:
        # iterate over every statement in the dict 
        for value in row['coverage'].values():
            # Only do this if the coverage statement has data on the date coverage
            if 'Available from' in value:
                # For coverage statements to the present
                if not any(s in value for s in ('Most recent', 'until')):
                    tempList.append((re.search(r"Available from (\d{4})", value).group(1)) + ' - present')
                # For coverage statements with an embargo
                if 'Most recent' in value:
                    tempList.append((re.search(r"Available from (\d{4})", value).group(1))  + ' - ' + re.search(r'Most recent (.*?)\(s\)', value).group(1) + ' ago')
                # For coverage statements that aren't current to the present
                if 'until' in value:
                    tempList.append((re.search(r"Available from (\d{4})", value).group(1)) + ' - ' + (re.search(r"until (\d{4})", value).group(1)))
    return pd.Series([tempList])




def coverageStatement_yearsParser2(row):
    '''
    (pd.Series) -> pd.Series
    
    This function takes the coverage statements provided by the link resolver, parses out the dates, and creates a one line date range of coverage.
    '''
    
    tempList = []
    # Don't do this if there are no coverage statements
    if row['coverage'] != {}:
        
        # iterate over every statement in the dict 
        for value in row['coverage'].values():
            
            # Only do this if the coverage statement has data on the date coverage
            if 'Available from' in value:
                
                # For coverage statements to the present
                if not any(s in value for s in ('Most recent', 'until')):
                    try:
                        tempList.append((re.search(r"Available from (\d{4})", value).group(1)) + ' - present')
                    except AttributeError:
                        tempList.append('?')
                    
                # For coverage statements with an embargo
                if 'Most recent' in value:
                    try:
                        tempList.append((re.search(r"Available from (\d{4})", value).group(1))  + ' - ' + re.search(r'Most recent (.*?)\(s\)', value).group(1) + ' ago')
                    except AttributeError:
                        tempList.append('?')
                # For coverage statements that aren't current to the present
                if 'until' in value:
                    try:
                        tempList.append((re.search(r"Available from (\d{4})", value).group(1)) + ' - ' + (re.search(r"until (\d{4})", value).group(1)))
                    except AttributeError:
                        tempList.append('?')
    return pd.Series([tempList])




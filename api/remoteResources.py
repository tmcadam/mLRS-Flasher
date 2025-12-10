#************************************************************
# Copyright (c) MLRS project
# GPL3
# https://www.gnu.org/licenses/gpl-3.0.de.html
# OlliW @ www.olliw.eu
#************************************************************
# mLRS Flasher Desktop App
# 30. Nov. 2025 001
#************************************************************

import json
import os
import re
import base64
from datetime import datetime as dt, timedelta as td

import requests

# url to file mlrs_firmware_urls.json, which hosts info on releases
g_firmware_json_url = 'https://raw.githubusercontent.com/olliw42/mLRS/refs/heads/main/tools/web/mlrs_firmware_urls.json'
# url to a release branch
g_repository_url = 'https://api.github.com/repos/olliw42/mLRS/git/trees/'
# url to main branch
g_main_branch_url = 'https://api.github.com/repos/olliw42/mLRS/git/trees/main'
# url to wirelessbridge ino.bin
g_wirelessbridge_path_url = 'https://raw.githubusercontent.com/olliw42/mLRS/refs/heads/main/firmware/wirelessbridge/'

# cache for github downloads
# g_jsonCacheDict = {}

def requestJsonDict(url, extension='', error_msg=''):

    # if url in g_jsonCacheDict.keys():
    #     print('* cached', url)
    #     return copy.deepcopy(g_jsonCacheDict[url])

    print('* request dict', url)
    res = None
    tries = 4
    while tries > 0:
        try:
            res = requests.get(url + extension, allow_redirects=True, timeout=(2,4))
            if b'API rate limit exceeded' in res.content:
                print(res.content)
                print('DONWLOAD FAILED!')
                print(error_msg)
                return False
            jsonDict = res.json()
            break # got it
        except Exception as e:
            raise e
            tries = tries - 1
            if tries < 0:
                if res: print(res.content)
                print(error_msg)
                return None

    # g_jsonCacheDict[url] = copy.deepcopy(jsonDict)
    return jsonDict


def requestData(url, error_msg=''):
    print('* request data', url)
    jsonDict = None
    tries = 4
    while tries > 0:
        try:
            res = requests.get(url, allow_redirects=True, timeout=(2,4))
            if b'API rate limit exceeded' in res.content:
                print(res.content)
                print('DONWLOAD FAILED!')
                print(error_msg)
                return False
            try:
                jsonDict = res.json()
            except:
                data = res.content
            break # got it
        except:
            tries = tries - 1
            if tries < 0:
                print(res.content)
                print(error_msg)
                return None
    if jsonDict:
        if jsonDict['encoding'] == 'base64':
            data = base64.b64decode(jsonDict['content'])
        else:
            data = jsonDict['content']
    return data


def find_files(prefix, folder):
    return [f for f in os.listdir(folder) if f.startswith(prefix)]

def read_cache(prefix, config_dir, max_age_hours=24):
    if not config_dir:
        return None
    cached_files = sorted(find_files(prefix, config_dir), reverse=True)
    if cached_files:
        latest_cache_file = cached_files[0]
        cache_filepath = os.path.join(config_dir, latest_cache_file)
        cache_ts_str = latest_cache_file.split("-")[-1].replace('.json','')
        cache_ts = dt.strptime(cache_ts_str, '%Y%m%d_%H%M%S')
        if dt.now() - cache_ts < td(hours=max_age_hours):
            try:
                with open(cache_filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                return data
            except:
                pass
    return None

def write_cache(prefix, data, config_dir):
    if not config_dir:
        return
    timestamp_str = dt.now().strftime('%Y%m%d_%H%M%S')
    cache_filename = f"{prefix}-{timestamp_str}.json"
    cache_filepath = os.path.join(config_dir, cache_filename)
    try:
        with open(cache_filepath, "w", encoding="utf-8") as f:
            json.dump(data, f)
    except:
        pass

def clean_cache(prefix, config_dir):
    cached_files = sorted(find_files(prefix, config_dir), reverse=True)
    for old_file in cached_files[1:]:
        try:
            os.remove(os.path.join(config_dir, old_file))
        except:
            pass

def requestJsonDictCached(url, extension='', error_msg='', config_dir=None, cache_prefix=None, max_age_hours=24):
    if not config_dir or not cache_prefix:
        return requestJsonDict(url, extension, error_msg)
    # check if we have a cached version, if not download
    resDict = read_cache(cache_prefix, config_dir, max_age_hours)
    if not resDict:
        resDict = requestJsonDict(url, extension, error_msg)
        if not resDict:
            return resDict
        print('* downloaded', url + extension)
        print('* caching', cache_prefix)
        write_cache(cache_prefix, resDict, config_dir)
        clean_cache(cache_prefix, config_dir)
    else:
        print('* using cached', cache_prefix)
    return resDict


# API for app
def downloadVersionsDict(config_dir=None):
    # download mlrs_firmware_urls.json
    # it holds the "released" versions, i.e., all non-dev versions
    # url = 'https://raw.githubusercontent.com/olliw42/mLRS/refs/heads/main/tools/web/mlrs_firmware_urls.json'

    # check if we have a cached version, if not download

    resDict = requestJsonDictCached(g_firmware_json_url, '', 'ERROR: downloadVersionsDict() [1]', config_dir, 'mlrs_firmware_urls', max_age_hours=24)
    if not resDict:
        return resDict
    #print(resDict)

    # manipulate resDict: add fields versionStr and gitUrl
    for key in list(resDict.keys()):
        v = key.split('.')
        patch = int(v[2])
        if patch == 0: # .00
            resDict[key]['versionStr'] = key + ' (release)'
        elif patch & 1 == 0: # even
            resDict[key]['versionStr'] = key + ' (pre-release)'
        elif patch & 1 > 0: # odd
            resDict[key]['versionStr'] = key + ' (dev)'
        else:
            resDict[key]['versionStr'] = key + ' (?)' # should not happen, play it safe

        # url = 'https://api.github.com/repos/olliw42/mLRS/git/trees/' + resDict[key]['commit'] + '?recursive=true'
        resDict[key]['gitUrl'] = g_repository_url + resDict[key]['commit']

    # Figure out also the pre-release dev version. This needs work:
    # We need to read the main json, to get the current firmware folder url,
    # then read one file name in this folder, and extract the version part from the file name.
    # url = 'https://api.github.com/repos/olliw42/mLRS/git/trees/main'
    res = requestJsonDictCached(g_main_branch_url, '', 'ERROR: downloadVersionsDict() [2]', config_dir, 'mlrs_github_main_branch', max_age_hours=24)
    if not res:
        return res
    resMainList = res['tree'] # it's a list of dictionaries
    #print(resMainList)

    firmwarePathDict = None
    for key in resMainList:
        if key['path'] == 'firmware':
            firmwarePathDict = key
            break
    if firmwarePathDict == None: # something is wrong, so go ahead with what we have
        return resDict
    #print(firmwarePathDict)

    url_main_firmware = firmwarePathDict['url'] # not so many, so we can afford getting them all
    res = requestJsonDictCached(url_main_firmware, '?recursive=true', 'ERROR: downloadVersionsDict() [3]', config_dir, 'mlrs_github_main_firmware', max_age_hours=24    )
    if not res:
        return res
    resMainFirmwareList = res['tree'] # it's a list of dictionaries
    #print(resMainFirmwareList)

    # firmware_filename looks like pre-release-stm32/rx-E77-MBLKit-wle5cc-400-tcxo-v1.3.01-@ae667b78.hex
    # find one file with a -@ in the name, and asumme it is representative for all dev versions
    # this means in all firmware/ subfolders only equal -@ must appear
    # regex to get version and commit
    for key in resMainFirmwareList:
        if '-@' in key['path']: # this is one
            #print('we got one')
            #print(key)
            #print(key['path'])
            f = re.search(r'-(v\d\.\d+?\.\d+?-@[A-Za-z0-9]+?)\.', key['path']) # TODO: doesn't correctly parse branch dev versions
            #print(f, f.group(1))
            if f:
                resDict[f.group(1)] = {
                    'versionStr' : f.group(1) + ' (dev)',
                    'gitUrl' : url_main_firmware # ??? ok ???
                }
            break

    #print(resDict)
    return resDict

# API for app
# Get files list from github repo, for a specifc tree, and filter according to what we want.
# pass in a GitHub tree URL like https://api.github.com/repos/olliw42/mLRS/git/trees/f12d680?recursive=true
# this is needed to get the list of files from the location which is specific to the version
def downloadFilesListFromTree(txrxlua, url, device='', version='', config_dir=None):
    res = requestJsonDictCached(url, '?recursive=true', 'ERROR: downloadFilesListFromTree() [1]', config_dir, 'mlrs_github_tree_' + version, max_age_hours=24  )
    if not res:
        return None
    resList = res['tree'] # it's a list of dictionaries
    if txrxlua == 'lua': # 'lua'
        for key in resList[:]: # creates a copy of the list, so we can easily remove
            if 'lua/' not in key['path']:
                resList.remove(key)
            elif key['type'] != 'blob': # seems to not be needed, as all 'lua/' seem to be blob
                resList.remove(key)
            elif '.lua' not in key['path']: # only accept files with '.lua' extension
                resList.remove(key)
    elif txrxlua == 'txint': # 'tx int'
        if device == '' or version == '': print('ERROR: downloadFilesListFromTree() [2]')
        #print(url, device, version)
        #print(resList)
        for key in resList[:]: # creates a copy of the list, so we can easily remove
            #if 'firmware/' not in key['path']:
            #    resList.remove(key)
            if key['type'] != 'blob':
                resList.remove(key)
            elif '-stm32' in key['path']: # remove all files with '-stm32'
                resList.remove(key)
            elif '-esp' not in key['path']: # only accept files with '-esp', should be redundant
                resList.remove(key)
            elif '-internal-' not in key['path']:
                resList.remove(key)
            elif version not in key['path']: # ensure we only have the desired firmware version
                resList.remove(key)
            elif device not in key['path']: # only accept tx-device-internal
                resList.remove(key)
    else: # 'tx' or 'rx'
        if device == '' or version == '': print('ERROR: downloadFilesListFromTree() [3]')
        #print(url, device, version)
        #print(resList)
        for key in resList[:]: # creates a copy of the list, so we can easily remove
            #if 'firmware/' not in key['path']:
            #    resList.remove(key)
            if key['type'] != 'blob': # seems to not be needed, as all 'firmware/' seem to be blob
                resList.remove(key)
            #elif '-esp' in key['path']: # remove all files with '-esp'
            #    resList.remove(key)
            #elif '-stm32' not in key['path']: # only accept files with '-stm32', should be redundant
            #    resList.remove(key)
            elif '-internal-' in key['path']:
                resList.remove(key)
            elif '-stm32' not in key['path'] and '-esp' not in key['path']: # only accept files with '-stm32' or '-esp'
                resList.remove(key)
            elif version not in key['path']: # ensure we only have the desired firmware version
                resList.remove(key)
            elif device not in key['path']: # only accept tx-device-xxx or rx-device-xxx
                resList.remove(key)

    ''' import pprint
    F = open('filesfromtree-'+txorrxortxintorlua+'.txt', 'w')
    F.write(url)
    F.write('\n\r')
    F.write( pprint.pformat(resList) )
    F.close() '''

    return resList


def downloadFileAndWriteToDisk(url, filename):
    #url = 'https://api.github.com/repos/olliw42/mLRS/git/blobs/9cfb92d2de3f0582b6b33279abecd941885681d4'
    #filename = 'rx-matek-mr24-30-g431kb-can-v1.3.04.hex'
    data = requestData(url, 'ERROR: downloadFileAndWriteToDisk()')
    F = open(filename, 'wb')
    F.write(data)
    F.close()
    return True

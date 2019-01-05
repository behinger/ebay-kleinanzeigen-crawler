#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from attrdict import AttrDict
import mechanicalsoup
import json

JSON_OUT = 'data/results.json'




def get_args():
    import argparse
    parser = argparse.ArgumentParser(description='Crawl ebay kleinanzeigen', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--url', default='https://www.ebay-kleinanzeigen.de/s-%s/%s/k0', help='The start url. Must have a [percent-sign]s portion in the url to insert the "options" like the page num, price etc.')
    parser.add_argument('--page-start', default=1, type=int, help='The page number to start at')
    parser.add_argument('--page-end', default=6, type=int, help='The page number to end at')
    parser.add_argument('--json-out', default=JSON_OUT, help='The path for the output json.')
    parser.add_argument('--options', default='', help='Options for kleinanzeigen. Get from the site')
    parser.add_argument('--target', default='', help='Kleinanzeigen Keyword')
    args = parser.parse_args()
    
    args.url = 'https://www.ebay-kleinanzeigen.de/s-%s/%s/k0'.format('%s',args.target)

    if not args.options == '':
        args.url = args.url % (args.options + '/%s')
    
    return args


def render(ads):
    from jinja2 import Template
    template = Template(open('index.html.tpl').read())
    with open('data/index.html', 'w') as f:
        f.write(template.render(ads=ads))


def get_results(browser, url, page_num):
    page = browser.get(url % ('seite:' + str(page_num)))
    print(url % ('seite:' + str(page_num)))
    # Dirty
    domain = '/'.join(url.split('/')[0:3])
    results = []
    for el in page.soup.select('article.aditem'):
        out = AttrDict()
        out.link = domain + el.select('a[href^="/s-anzeige"]')[0].attrs['href']
        out.title = el.select('.text-module-begin a')[0].text.strip()
        out.desc = el.select('.aditem-main p')[0].text.strip()
        addetails = el.select('.aditem-details')[0]
        out.price = addetails.select('strong')[0].text.strip()
        out.added = el.select('.aditem-addon')[0].text.strip()
        
        img = el.select('[data-imgsrc]')
        out.img = img[0].attrs['data-imgsrc'] if len(img) else None
        results.append(out)
    return results

def manual_call(target = "schifferklavier",page_start=1,page_end=5,jsonout=JSON_OUT):
    arg = AttrDict()
    arg.page_start = page_start
    arg.page_end = page_end
    arg.json_out = jsonout
    print(target)
    arg.target = target
    arg.url = 'https://www.ebay-kleinanzeigen.de/s-%s/k0'.format('%s/'+arg.target)
    run_program(arg)
    
def run_program(args):
    browser = mechanicalsoup.Browser(soup_config=({'features':"html.parser"}))
    results = []
    print("Starting to crawl. Options:\n{}\n".format(args))
    for page_num in range(args.page_start, args.page_end + 1):
        print("\tCrawling page: {}/{}".format(page_num, args.page_end))
        results += get_results(browser, args.url, page_num)
    with open(args.json_out, 'w') as f:
        json.dump(results, f, indent=4, sort_keys=True)
    #print(results)
    #render(results)
    import urllib.request
    img_urls = [r['img'] for r in results if r is not None]
    import os
    
    try:
        os.mkdir('data/{}'.format(args.target))
    except:
        pass
        
    for idx,img in enumerate(img_urls):
        try:
            urllib.request.urlretrieve(img, "data/{}/{}.jpg".format(args.target,idx))
        except TypeError:
            pass
            
def main():
    args = get_args()
    run_program(args)
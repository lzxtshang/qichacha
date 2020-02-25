#! /usr/bin/env python3
# -*- coding:utf-8 -*-

"""
企查查-专利信息
"""
import time
import random
import requests

from lxml import etree

from support.use_mysql import ConnMysql as db
from support.others import DealKey as dk
from support.others import TimeInfo as tm
from support.headers import GeneralHeaders as gh

class PatentInfo():

    def get_com_id(self):
        # sel = """
        # SELECT `com_id`,`com_name`,`status_patent`,`count_patent`
        # FROM `com_info`
        # WHERE `origin`
        # IS NOT NULL AND LENGTH(`com_id`) > 8 AND `status_patent` IS NULL AND `count_patent` != '0'
        # ORDER BY RAND() LIMIT 1;
        # """
        # sel ="""
        # SELECT `com_id`,`com_name`,`status_patent`,`count_patent`
        # FROM `com_info`
        # WHERE `com_id` IN
        # (
        # '06b9ede70996255ed343050895046d00',
        # '09a2b97c0596a84cf14404a4bd2c37d5',
        # '18ff2c7ad1d11bfe40e0bec84f6d04d3',
        # '1b16bbdae1540c6a72cd81d918b7c1f6',
        # '30c09ef2def97bd3dc8d021fc2233b05',
        # '31755ff79f6e867d79f7e49cb34da867',
        # '424b1559bdac92d298cf9751979eb26b',
        # '48431ef3f2c62cc60e1f4c22a178ee50',
        # '4c468b205f73f703274e9db7f769a03f',
        # '5602135acdc60cd54daf58cffbc24367',
        # '61b780963a4bc4df5707fe376e41fb6f',
        # '652177a5d80be3d70d7460a09018f599',
        # '722e57a557a857c16121d5c03bd06d42',
        # '7bb7f10fbffbdb6af869af34e8697ecc',
        # '89d337c3d33410e68ca65d7933bd7d05',
        # '8ad8b2d2c15fb92f9ce14107489e83cd',
        # '9779771217b77e4538bd505660939c9a',
        # '9b0c52e7af1ee199857b94bc3ea6be3d',
        # 'a484e7a0b3167f6b257beb51dd93b241',
        # 'a58533710987ecf98159545b61505a74',
        # 'a5a0ba522ce994fb2a8de3a7625534e1',
        # 'a9aa7de83d5d7b4c5008310395b1f403',
        # 'ad797adc3b0a3fe293a0d7238c671b72',
        # 'af8ef0be6adcc6cc6c5b5d1c217b487c',
        # 'b45f3cc43a98aa52f5b3409cef1d6cd9',
        # 'd3d4ff0894e82ca22a9e6b3a66fda267',
        # 'dbe7a5624002aec7b0f26445c94f60cc',
        # 'e06f5af040745430aec2faf8684ae3c7',
        # 'f11933e8723fd03d325529bd2adc19a6',
        # 'fa078a468930c63c92f7909b5a1c5788',
        # 'ff0e1ff937b7aaa29b8953a54c978fe8'
        # )
        # AND `status_patent` IS NULL AND `count_patent` != '0'
        # ORDER BY RAND() LIMIT 1;
        # """
        # sel = """
        # SELECT `com_id`,`com_name`,`status_patent`,`count_patent`
        # FROM `com_info`
        # WHERE `origin` = '崂山区虚拟现实企业90家数据相关'
        # AND LENGTH(`com_id`) > 5 AND `status_patent` IS NULL AND `count_patent` != '0'
        # ORDER BY RAND() LIMIT 1;
        # """
        # sel = """
        # SELECT b.`com_id`,b.`com_name`,b.`status_patent`,b.`count_patent`
        # FROM temp_ppp a JOIN com_info b
        # ON a.`com_name`=b.`com_name`
        # AND LENGTH(b.com_id)=32
        # AND b.`status_patent` IS NULL
        # AND count_patent != 0
        # ORDER BY RAND() LIMIT 1;
        # """
        sel = """
        SELECT com_id,com_name,status_patent,count_patent 
        FROM com_info WHERE status_patent IS NULL
        AND count_patent != 0
        AND `other_id` LIKE '%ls1000%'
        ORDER BY RAND() LIMIT 1;
        """
        result = db().selsts(sel)
        if result == ():
            result = [None,None,None,None]
        else:
            result = result[0]
        return result

    def get_page_count(self): #获取页面页数
        pt = PatentInfo()
        result = pt.get_com_id()
        com_id = result[0]
        com_name = result[1]
        key = dk().search_key(com_name)
        status = result[2]
        if com_id == None:
            value = [None,None,None,None]
        else:
            index_url = 'https://www.qichacha.com'
            com_url = f'{index_url}/company_getinfos?unique={com_id}&companyname={key}&tab=assets'
            hds = gh().header()
            hds.update({'Referer': f'{index_url}/firm_{com_id}.html'})
            time.sleep(random.randint(1,2))
            res = requests.get(com_url,headers=hds).text
            if '<script>window.location.href' in res:
                print('访问频繁，需验证！{get_page_count}')
                input('暂停')
            elif '<script>location.href="/user_login"</script>' in res:
                print('Cookie失效，需更换！{get_page_count}')
                input('程序暂停运行！')
            elif '您的账号访问超频，请稍后访问或联系客服人员' in res:
                print('账号访问超频，请更换账号！{get_page_count}')
                input('程序暂停运行！')
            else:
                tree = etree.HTML(res)
                try:
                    count_patent = tree.xpath('//*[contains(text(),"专利信息") and @class="title"]/following-sibling::span[@class="tbadge"]/text()')[0].strip()
                except:
                    count_patent = tree.xpath('//section[@id="zhuanlilist"]//*[@class="tbadge"]/text()')[0].strip()
                if count_patent == '5000+':
                    count_page = 500
                else:
                    count_patent = int(count_patent)
                    if count_patent%10 == 0:
                        count_page = count_patent//10
                    else:
                        count_page = count_patent//10 + 1
                value = [com_id,com_name,count_page,index_url]
        return value

    def get_page_info(self): #获取页面详情
        pt = PatentInfo()
        value = pt.get_page_count()
        com_id = value[0]
        com_name = value[1]
        count_page = value[2]

        # 临时代码，供单次补采数据【001】
        # com_id = 'x697654f34422233895571cf26e42268'
        # com_name = '青岛科技大学'
        # count_page = 500
        # 临时代码，供单次补采数据【001】

        if com_id == None:
            pass
        else:
            key = dk().search_key(com_name)
            index_url = value[3]
            count = 0
            start_time = tm().get_localtime() #当前时间
            for page in range(1, count_page + 1): #临时代码，供单次补采数据【001】
            # for page in range(1, count_page + 1):
            #     if page == 1:
            #         page_url = f'https://www.qichacha.com/company_getinfos?unique={com_id}&companyname={com_name}&tab=assets'
                page_url = f'{index_url}/company_getinfos?unique={com_id}&companyname={key}&p={page}&tab=assets&box=zhuanli'
                hds = gh().header()
                hds.update({'Referer': f'{index_url}/firm_{com_id}.html'})
                time.sleep(random.randint(1,2))
                res_pg = requests.get(page_url, headers=hds).text
                if '<script>window.location.href' in res_pg:
                    print('访问频繁，需验证！{get_page_info[1]}')
                    input('暂停')
                elif '<script>location.href="/user_login"</script>' in res_pg:
                    print('Cookie失效，需更换！{get_page_info[1]}')
                    input('程序暂停运行！')
                elif '您的账号访问超频，请稍后访问或联系客服人员' in res_pg:
                    print('账号访问超频，请更换账号！{get_page_info[1]}')
                    input('程序暂停运行！')
                else:
                    tree_pg = etree.HTML(res_pg)
                    content_li = tree_pg.xpath('//table/tr[position()>1]')
                    for content in content_li:
                        count += 1
                        patent_num = content.xpath('td[1]/text()')[0]
                        patent_type = content.xpath('td[2]/text()')[0]
                        patent_pub_num = content.xpath('td[3]/text()')[0]
                        patent_pub_date = content.xpath('td[4]/text()')[0]
                        patent_name = content.xpath('td[5]/a/text()')[0].strip()
                        patent_link = content.xpath('td[5]/a/@href')[0]
                        patent_id = patent_link.split('_com_')[1]
                        patent_url = ''.join((index_url,patent_link))
                        time.sleep(random.randint(1,3))
                        res_dt = requests.get(patent_url,headers=hds).text
                        if '<script>window.location.href' in res_dt:
                            print('访问频繁，需验证！{get_page_info[2]}')
                            input('暂停')
                        elif '<script>location.href="/user_login"</script>' in res_dt:
                            print('Cookie失效，需更换！{get_page_info[2]}')
                            input('程序暂停运行！')
                        elif '您的账号访问超频，请稍后访问或联系客服人员' in res_dt:
                            print('账号访问超频，请更换账号！{get_page_info[2]}')
                            input('程序暂停运行！')
                        else:
                            tree_dt = etree.HTML(res_dt)
                            app_num = tree_dt.xpath('//table[@class="ntable"]/tbody/tr/td[contains(text(),"申请号")]/following-sibling::td[1]/text()')[0].strip()
                            app_date = tree_dt.xpath('//table[@class="ntable"]/tbody/tr/td[contains(text(),"申请日")]/following-sibling::td[1]/text()')[0].strip()
                            prio_date = tree_dt.xpath('//table[@class="ntable"]/tbody/tr/td[contains(text(),"优先权日")]/following-sibling::td[1]/text()')[0].strip()
                            prio_num = tree_dt.xpath('//table[@class="ntable"]/tbody/tr/td[contains(text(),"优先权号")]/following-sibling::td[1]/text()')[0].strip()
                            inventor = tree_dt.xpath('//table[@class="ntable"]/tbody/tr/td[contains(text(),"发明人")]/following-sibling::td[1]/text()')[0].strip()
                            try:
                                applicant = tree_dt.xpath('//table[@class="ntable"]/tbody/tr/td[contains(text(),"申请（专利权）人")]/following-sibling::td[1]/a/text()')[0].strip()
                            except:
                                applicant = tree_dt.xpath('//table[@class="ntable"]/tbody/tr/td[contains(text(),"申请（专利权）人")]/following-sibling::td[1]')[0].strip()
                            try:
                                agency = tree_dt.xpath('//table[@class="ntable"]/tbody/tr/td[contains(text(),"代理机构")]/following-sibling::td[1]/a/text()')[0].strip()
                            except:
                                agency = tree_dt.xpath('//table[@class="ntable"]/tbody/tr/td[contains(text(),"代理机构")]/following-sibling::td[1]/text()')[0].strip()
                            agent = tree_dt.xpath('//table[@class="ntable"]/tbody/tr/td[contains(text(),"代理人")]/following-sibling::td[1]/text()')[0].strip()
                            ipc = tree_dt.xpath('//table[@class="ntable"]/tbody/tr/td[contains(text(),"IPC分类号")]/following-sibling::td[1]/text()')[0].strip().replace(' ','').replace('\n','')
                            cpc = tree_dt.xpath('//table[@class="ntable"]/tbody/tr/td[contains(text(),"CPC分类号")]/following-sibling::td[1]/text()')[0].strip()
                            app_address = tree_dt.xpath('//table[@class="ntable"]/tbody/tr/td[contains(text(),"申请人地址")]/following-sibling::td[1]/text()')[0].strip()
                            app_zip_code = tree_dt.xpath('//table[@class="ntable"]/tbody/tr/td[contains(text(),"申请人邮编")]/following-sibling::td[1]/text()')[0].strip()
                            try:
                                abstract = tree_dt.xpath('//table[@class="ntable"]/tbody/tr/td[contains(text(),"摘要")]/following-sibling::td[1]/text()')[0].strip()
                            except:
                                abstract = tree_dt.xpath('string(//table[@class="ntable"]/tbody/tr/td[contains(text(),"摘要")]/following-sibling::td)').strip()
                            try:
                                abstract_photo = tree_dt.xpath('//table[@class="ntable"]/tbody/tr/td[contains(text(),"摘要附图")]/following-sibling::td[1]/img/@src')[0].strip()
                            except:
                                abstract_photo = '-'
                            try:
                                claim = tree_dt.xpath('//table[@class="ntable"]/tr/td[@class="ea_instructions" and position()=1]/p/text()')
                                claim = ''.join(claim).replace('"',"'")
                            except:
                                claim = '-'
                            try:
                                instructions = tree_dt.xpath('//div[@class="tcaption"]/h3[text()="说明书"]/parent::div/following-sibling::table[@class="ntable"]/tr/td[@class="ea_instructions"]/h1/text()|//div[@class="tcaption"]/h3[text()="说明书"]/parent::div/following-sibling::table[@class="ntable"]/tr/td[@class="ea_instructions"]/h2/text()|//div[@class="tcaption"]/h3[text()="说明书"]/parent::div/following-sibling::table[@class="ntable"]/tr/td[@class="ea_instructions"]/p/text()')
                                instructions = ''.join(instructions)
                            except:
                                instructions = '-'
                            print('\n{0}--总第{1}条----{2}/{3}页--{0}\n'.format('-' * 9, count,page,count_page))
                            localtime = tm().get_localtime()  # 当前时间
                            create_time = localtime
                            print(f'公司ID:{com_id} 当前时间：{localtime}')
                            print(f'公司名称：{com_name}\n专利ID：{patent_id}')
                            print(f'序号:{patent_num}\n专利类型:{patent_type}\n公开（公告）号:{patent_pub_num}\n公开（公告）日期:{patent_pub_date}\n专利名称:{patent_name}\n'
                                  f'专利页URL:{patent_url}\n申请号:{app_num}\n申请日期:{app_date}\n优先权日:{prio_date}\n优先权号:{prio_num}\n'
                                  f'发明人:{inventor}\n申请（专利权）人:{applicant}\n代理机构:{agency}\n代理人:{agent}\nIPC分类号:{ipc}\n'
                                  f'CPC分类号:{cpc}\n申请人地址:{app_address}\n申请人邮编:{app_zip_code}\n摘要:{abstract}\n摘要附图:{abstract_photo}\n'
                                  f'权利要求:{claim}\n说明书:{instructions}\n')
                            ins = f"""
                            INSERT INTO  
                            `com_patent`
                            (`com_id`,`patent_num`,`patent_type`,`patent_pub_num`,`patent_pub_date`,
                            `patent_name`,`patent_url`,`app_num`,`app_date`,`prio_date`,
                            `prio_num`,`inventor`,`applicant`,`agency`,`agent`,
                            `ipc`,`cpc`,`app_address`,`app_zip_code`,`abstract`,`abstract_photo`,
                            `claim`,`instructions`,`create_time`,`patent_id`)
                            VALUES 
                            ("{com_id}","{patent_num}","{patent_type}","{patent_pub_num}","{patent_pub_date}",
                            "{patent_name}","{patent_url}","{app_num}","{app_date}","{prio_date}",
                            "{prio_num}","{inventor}","{applicant}","{agency}","{agent}",
                            "{ipc}","{cpc}","{app_address}","{app_zip_code}","{abstract}","{abstract_photo}",
                            "{claim}","{instructions}","{create_time}","{patent_id}");
                            """
                            db().inssts(ins)

                            upd = f"""
                            UPDATE 
                            `com_info` 
                            SET
                            `status_patent` = 1
                            WHERE 
                            `com_id` = "{com_id}" ;
                            """
                            db().updsts(upd)
            localtime = tm().get_localtime()  # 当前时间
            print('\n{1}\n{0}数据采集完成!{0}\n{1}'.format('+' * 7, '+' * 25))
            print(f'当前时间：{localtime}\n')
            time.sleep(3)


    def run(self):
        pt = PatentInfo()
        while 1 == 1:
            print('Loading......\n')
            time.sleep(5)
            print('开始新一轮采集')
            pt.get_page_info()


if __name__ == '__main__':
    pt = PatentInfo()
    # pt.get_com_id()
    while 1 == 1:
        print('Loading......\n')
        time.sleep(5)
        print('开始新一轮采集')
        pt.get_page_info()
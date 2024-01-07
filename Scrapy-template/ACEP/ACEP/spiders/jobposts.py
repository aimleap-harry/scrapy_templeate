import re
import scrapy
import dateparser
import datetime



class JobPostsSpider(scrapy.Spider):
    name = 'jobposts'   

    def start_requests(self):
        LIMIT_DAYS = int(self.settings.get('LIMIT_DAYS'))
        TODAY = datetime.datetime.today()
        self.LIMIT_DAY = TODAY - datetime.timedelta(days=LIMIT_DAYS)
        self.logger.info(f"Limiting day to: {str(self.LIMIT_DAY)}")

        url = "https://www.emcareers.org/jobs/1/"
        yield scrapy.Request(url, callback=self.parse, meta={ "is_first":True} )


    def parse(self, response):
        limit_reached = False
        posts = response.xpath('//ul[@id="listing"]/li[@id]')
        for post in posts:
            post_url = post.xpath('.//h3/a/@href').get('').strip()
            post_url ="https://www.emcareers.org" + post_url
            posted_on = post.xpath('.//li[contains(@class,"actions__action pipe")]/text()').get()
            try:
                posted_on = dateparser.parse(posted_on)
            except:
                posted_on = ''
            
            if posted_on and posted_on > self.LIMIT_DAY:
                yield scrapy.Request(post_url, callback=self.get_all_data, meta={"posted_on": posted_on.strftime('%Y-%m-%d')})
            else:
                limit_reached=True
        
        next = response.xpath('//a[@rel="next"]/@href').get()
        if next and not limit_reached:
            yield response.follow(next)


    def get_all_data(self,response):

        post_url = response.url
        post_title = response.xpath('//h1/text()').get()
        posted_on = response.meta['posted_on']

        try:
            company_name = response.xpath("//dt[contains(text(),'Employer')]//following-sibling::dd[@class='mds-list__value']//text()").get().strip()
            if not company_name:
                company_name = response.xpath("//dt[contains(text(),'Employer')]//following-sibling::dd[@class='mds-list__value']/a//text()").get().strip()
        except:
            company_name = ''
        try:
            location = (response.xpath('//dt[contains(text(),"Location")]//following-sibling::dd[@class="mds-list__value"]//text()').get())
        except:
            location = ''
        try:
            Salary_Details = response.xpath('//dt[contains(text(),"Salary")]//following-sibling::dd[@class="mds-list__value"]//text()').get().strip()
        except:
            Salary_Details = ''
        try:
            Closing_date = response.xpath("//dt[contains(text(),'Closing date')]//following-sibling::dd[@class='mds-list__value']//text()").get()
            try:
                Closing_date = datetime.datetime.strptime(Closing_date, '%b %d, %Y').strftime('%Y-%m-%d')
            except:
                Closing_date = dateparser.parse(Closing_date.strip()).strftime('%Y-%m-%d')
        except:
            Closing_date = ''

        Specialty_one = response.xpath("//dt[contains(text(),'Specialty / Focus')]//following-sibling::dd[@class='mds-list__value']//a[1]//text()").get()
        Specialty_two = response.xpath("//dt[contains(text(),'Specialty / Focus')]//following-sibling::dd[@class='mds-list__value']//a[2]//text()").get()
        if Specialty_one and Specialty_two:
            Specialty = Specialty_one + "," + Specialty_two
        else:
            Specialty = response.xpath("//dt[contains(text(),'Specialty / Focus')]//following-sibling::dd[@class='mds-list__value']//text()").get()

        Position_one = response.xpath("//dt[contains(text(),'Position Type')]//following-sibling::dd[@class='mds-list__value']//a[1]//text()").get()
        Position_two = response.xpath("//dt[contains(text(),'Position Type')]//following-sibling::dd[@class='mds-list__value']//a[2]//text()").get()
        if Position_two and Position_one:
            Position_type = Position_one + "," + Position_two
        else:
            Position_type = response.xpath("//dt[contains(text(),'Position Type')]//following-sibling::dd[@class='mds-list__value']//text()").get()

        try:
            Practise_type = response.xpath("//dt[contains(text(),'Practice Type')]//following-sibling::dd[@class='mds-list__value']//text()").get()
        except:
            Practise_type = ''
        
        Practise_setting_one = response.xpath("//dt[contains(text(),'Practice Setting')]//following-sibling::dd[@class='mds-list__value']//a[1]//text()").get()
        Practise_setting_two = response.xpath("//dt[contains(text(),'Practice Setting')]//following-sibling::dd[@class='mds-list__value']//a[2]//text()").get()
        if Practise_setting_one and Practise_setting_two:
            Practise_setting = Practise_setting_one + "," + Practise_setting_two
        else:
            Practise_setting = response.xpath("//dt[contains(text(),'Practice Setting')]//following-sibling::dd[@class='mds-list__value']//text()").get()
        
        try:
            Benefits = response.xpath("//dt[contains(text(),'Benefits')]//following-sibling::dd[@class='mds-list__value']//text()").get()
        except:
            Benefits = ''
        try:
            Work_Mode = response.xpath("//dt[contains(text(),'Hours')]//following-sibling::dd[@class='mds-list__value']//text()").get()
        except:
            Work_Mode = ''
        try:
            Employment_type = response.xpath("//dt[contains(text(),'Employment Type')]//following-sibling::dd[@class='mds-list__value']//text()").get()
        except:
            Employment_type = ''
        try:
            Patient_care_type = response.xpath("//dt[contains(text(),'Patient Care')]//following-sibling::dd[@class='mds-list__value']//text()").get()
        except:
            Patient_care_type = ''
        try:
            job_detai = ' '.join(response.xpath("//div[contains(@class,'mds-edited-text mds-font-body-copy-bulk')]//text()").getall()).strip().replace('\r\n', '')
            def ascii_sign(sing_replacement):
                replace_rext = re.sub(r'[^\x00-\x7f]',"",sing_replacement)
                return replace_rext
            job_details = ascii_sign(job_detai)
        except:
            job_details = ''

        domainname = post_url.split('https://')[1].split('/')[0].replace('www.', '')
        job_id = post_url.split('/job/')[1].split('/')[0]
        yield{
            "Domain":domainname,
            "JobID": job_id,
            "PostUrl":post_url,
            "Title": post_title,
            "Company":company_name,
            "Location":location,
            "SalaryRange":Salary_Details,
            "PostedOn": posted_on,
            "LastDate":Closing_date,
            "Speciality":Specialty,
            "PositionType":Position_type,
            "PractiseType":Practise_type,
            "PractiseSetting":Practise_setting,
            "Benefits":Benefits,
            "JobType":Work_Mode,
            "EmploymentType":Employment_type,
            "PatientCareType":Patient_care_type,
            "JobDetails":job_details
        }
import requests, logging, json, threading, os, csv, pandas, sys, random
from datetime import date



class RMPScraper:
    if not os.path.exists("./logs/"):os.makedirs("./logs/")
    logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(levelname)s:%(name)s:%(message)s',
        handlers=[logging.FileHandler(f"./logs/rmp_scraper_log_{date.today()}.log"), 
        logging.StreamHandler(sys.stdout)])
    logging.info(" ========= RMP Scraper Bot Started =========")


    URL = 'https://www.ratemyprofessors.com/graphql'


    TEACHERS_QUERY_INIT = {
        "query": "query TeacherSearchResultsPageQuery(\n  $query: TeacherSearchQuery!\n  $schoolID: ID\n) {\n  "
                 "search: newSearch {\n    ...TeacherSearchPagination_search_1ZLmLD\n  }\n  school: node(id: "
                 "$schoolID) {\n    __typename\n    ... on School {\n      name\n    }\n    id\n  "
                 "}\n}\n\nfragment TeacherSearchPagination_search_1ZLmLD on newSearch {\n  teachers(query: "
                 "$query, first: 8, after: \"\") {\n    didFallback\n    edges {\n      cursor\n      node {\n    "
                 "    ...TeacherCard_teacher\n        id\n        __typename\n      }\n    }\n    pageInfo {\n    "
                 "  hasNextPage\n      endCursor\n    }\n    resultCount\n    filters {\n      field\n      "
                 "options {\n        value\n        id\n      }\n    }\n  }\n}\n\nfragment TeacherCard_teacher on "
                 "Teacher {\n  id\n  legacyId\n  avgRating\n  numRatings\n  ...CardFeedback_teacher\n  "
                 "...CardSchool_teacher\n  ...CardName_teacher\n  ...TeacherBookmark_teacher\n}\n\nfragment "
                 "CardFeedback_teacher on Teacher {\n  wouldTakeAgainPercent\n  avgDifficulty\n}\n\nfragment "
                 "CardSchool_teacher on Teacher {\n  department\n  school {\n    name\n    id\n  }\n}\n\nfragment "
                 "CardName_teacher on Teacher {\n  firstName\n  lastName\n}\n\nfragment TeacherBookmark_teacher "
                 "on Teacher {\n  id\n  isSaved\n}\n",
        "variables": {"query":
                          {"text": "", "schoolID": "U2Nob29sLTEwNzQ=", "fallback": True, "departmentID": None},
                      "schoolID": "U2Nob29sLTEwNzQ="}
    }

    TEACHERS_QUERY_PAGINATION = {
        "query": "query TeacherSearchPaginationQuery(\n  $count: Int!\n  $cursor: String\n  $query: "
                 "TeacherSearchQuery!\n) {\n  search: newSearch {\n    "
                 "...TeacherSearchPagination_search_1jWD3d\n  }\n}\n\nfragment "
                 "TeacherSearchPagination_search_1jWD3d on newSearch {\n  teachers(query: $query, "
                 "first: $count, after: $cursor) {\n    didFallback\n    edges {\n      cursor\n      node {\n  "
                 "      ...TeacherCard_teacher\n        id\n        __typename\n      }\n    }\n    pageInfo {"
                 "\n      hasNextPage\n      endCursor\n    }\n    resultCount\n    filters {\n      field\n    "
                 "  options {\n        value\n        id\n      }\n    }\n  }\n}\n\nfragment "
                 "TeacherCard_teacher on Teacher {\n  id\n  legacyId\n  avgRating\n  numRatings\n  "
                 "...CardFeedback_teacher\n  ...CardSchool_teacher\n  ...CardName_teacher\n  "
                 "...TeacherBookmark_teacher\n}\n\nfragment CardFeedback_teacher on Teacher {\n  "
                 "wouldTakeAgainPercent\n  avgDifficulty\n}\n\nfragment CardSchool_teacher on Teacher {\n  "
                 "department\n  school {\n    name\n    id\n  }\n}\n\nfragment CardName_teacher on Teacher {\n  "
                 "firstName\n  lastName\n}\n\nfragment TeacherBookmark_teacher on Teacher {\n  id\n  "
                 "isSaved\n}\n",
        "variables": {"count": 8, "cursor": "YXJyYXljb25uZWN0aW9uOjc=",
                      "query":
                          {"text": "", "schoolID": "U2Nob29sLTEwNzQ=", "fallback": False, "departmentID": None}}
    }      # Made fallback False to avoid trailing teachers from other UNIs when fallback happens

    RATINGS_QUERY_INIT = {
        "query": "query TeacherRatingsPageQuery(\n  $id: ID!\n) {\n  node(id: $id) {\n    __typename\n    ... on "
                 "Teacher {\n      id\n      legacyId\n      firstName\n      lastName\n      school {\n        "
                 "legacyId\n        name\n        id\n      }\n      lockStatus\n      ...StickyHeader_teacher\n  "
                 "    ...RatingDistributionWrapper_teacher\n      ...TeacherMetaInfo_teacher\n      "
                 "...TeacherInfo_teacher\n      ...SimilarProfessors_teacher\n      "
                 "...TeacherRatingTabs_teacher\n    }\n    id\n  }\n}\n\nfragment StickyHeader_teacher on Teacher "
                 "{\n  ...HeaderDescription_teacher\n  ...HeaderRateButton_teacher\n}\n\nfragment "
                 "RatingDistributionWrapper_teacher on Teacher {\n  ...NoRatingsArea_teacher\n  "
                 "ratingsDistribution {\n    total\n    ...RatingDistributionChart_ratingsDistribution\n  "
                 "}\n}\n\nfragment TeacherMetaInfo_teacher on Teacher {\n  legacyId\n  firstName\n  lastName\n  "
                 "department\n  school {\n    name\n    city\n    state\n    id\n  }\n}\n\nfragment "
                 "TeacherInfo_teacher on Teacher {\n  id\n  lastName\n  numRatings\n  ...RatingValue_teacher\n  "
                 "...NameTitle_teacher\n  ...TeacherTags_teacher\n  ...NameLink_teacher\n  "
                 "...TeacherFeedback_teacher\n  ...RateTeacherLink_teacher\n}\n\nfragment "
                 "SimilarProfessors_teacher on Teacher {\n  department\n  relatedTeachers {\n    legacyId\n    "
                 "...SimilarProfessorListItem_teacher\n    id\n  }\n}\n\nfragment TeacherRatingTabs_teacher on "
                 "Teacher {\n  numRatings\n  courseCodes {\n    courseName\n    courseCount\n  }\n  "
                 "...RatingsList_teacher\n  ...RatingsFilter_teacher\n}\n\nfragment RatingsList_teacher on "
                 "Teacher {\n  id\n  legacyId\n  lastName\n  numRatings\n  school {\n    id\n    legacyId\n    "
                 "name\n    city\n    state\n    avgRating\n    numRatings\n  }\n  ...Rating_teacher\n  "
                 "...NoRatingsArea_teacher\n  ratings(first: 20) {\n    edges {\n      cursor\n      node {\n     "
                 "   ...Rating_rating\n        id\n        __typename\n      }\n    }\n    pageInfo {\n      "
                 "hasNextPage\n      endCursor\n    }\n  }\n}\n\nfragment RatingsFilter_teacher on Teacher {\n  "
                 "courseCodes {\n    courseCount\n    courseName\n  }\n}\n\nfragment Rating_teacher on Teacher {"
                 "\n  ...RatingFooter_teacher\n  ...RatingSuperHeader_teacher\n  "
                 "...ProfessorNoteSection_teacher\n}\n\nfragment NoRatingsArea_teacher on Teacher {\n  lastName\n "
                 " ...RateTeacherLink_teacher\n}\n\nfragment Rating_rating on Rating {\n  comment\n  flagStatus\n "
                 " createdByUser\n  teacherNote {\n    id\n  }\n  ...RatingHeader_rating\n  "
                 "...RatingSuperHeader_rating\n  ...RatingValues_rating\n  ...CourseMeta_rating\n  "
                 "...RatingTags_rating\n  ...RatingFooter_rating\n  ...ProfessorNoteSection_rating\n}\n\nfragment "
                 "RatingHeader_rating on Rating {\n  date\n  class\n  helpfulRating\n  clarityRating\n  "
                 "isForOnlineClass\n}\n\nfragment RatingSuperHeader_rating on Rating {\n  legacyId\n}\n\nfragment "
                 "RatingValues_rating on Rating {\n  helpfulRating\n  clarityRating\n  "
                 "difficultyRating\n}\n\nfragment CourseMeta_rating on Rating {\n  attendanceMandatory\n  "
                 "wouldTakeAgain\n  grade\n  textbookUse\n  isForOnlineClass\n  isForCredit\n}\n\nfragment "
                 "RatingTags_rating on Rating {\n  ratingTags\n}\n\nfragment RatingFooter_rating on Rating {\n  "
                 "id\n  comment\n  adminReviewedAt\n  flagStatus\n  legacyId\n  thumbsUpTotal\n  "
                 "thumbsDownTotal\n  thumbs {\n    userId\n    thumbsUp\n    thumbsDown\n    id\n  }\n  "
                 "teacherNote {\n    id\n  }\n}\n\nfragment ProfessorNoteSection_rating on Rating {\n  "
                 "teacherNote {\n    ...ProfessorNote_note\n    id\n  }\n  "
                 "...ProfessorNoteEditor_rating\n}\n\nfragment ProfessorNote_note on TeacherNotes {\n  comment\n  "
                 "...ProfessorNoteHeader_note\n  ...ProfessorNoteFooter_note\n}\n\nfragment "
                 "ProfessorNoteEditor_rating on Rating {\n  id\n  legacyId\n  class\n  teacherNote {\n    id\n    "
                 "teacherId\n    comment\n  }\n}\n\nfragment ProfessorNoteHeader_note on TeacherNotes {\n  "
                 "createdAt\n  updatedAt\n}\n\nfragment ProfessorNoteFooter_note on TeacherNotes {\n  legacyId\n  "
                 "flagStatus\n}\n\nfragment RateTeacherLink_teacher on Teacher {\n  legacyId\n  numRatings\n  "
                 "lockStatus\n}\n\nfragment RatingFooter_teacher on Teacher {\n  id\n  legacyId\n  lockStatus\n  "
                 "isProfCurrentUser\n}\n\nfragment RatingSuperHeader_teacher on Teacher {\n  firstName\n  "
                 "lastName\n  legacyId\n  school {\n    name\n    id\n  }\n}\n\nfragment "
                 "ProfessorNoteSection_teacher on Teacher {\n  ...ProfessorNote_teacher\n  "
                 "...ProfessorNoteEditor_teacher\n}\n\nfragment ProfessorNote_teacher on Teacher {\n  "
                 "...ProfessorNoteHeader_teacher\n  ...ProfessorNoteFooter_teacher\n}\n\nfragment "
                 "ProfessorNoteEditor_teacher on Teacher {\n  id\n}\n\nfragment ProfessorNoteHeader_teacher on "
                 "Teacher {\n  lastName\n}\n\nfragment ProfessorNoteFooter_teacher on Teacher {\n  legacyId\n  "
                 "isProfCurrentUser\n}\n\nfragment SimilarProfessorListItem_teacher on RelatedTeacher {\n  "
                 "legacyId\n  firstName\n  lastName\n  avgRating\n}\n\nfragment RatingValue_teacher on Teacher {"
                 "\n  avgRating\n  numRatings\n  ...NumRatingsLink_teacher\n}\n\nfragment NameTitle_teacher on "
                 "Teacher {\n  id\n  firstName\n  lastName\n  department\n  school {\n    legacyId\n    name\n    "
                 "id\n  }\n  ...TeacherDepartment_teacher\n  ...TeacherBookmark_teacher\n}\n\nfragment "
                 "TeacherTags_teacher on Teacher {\n  lastName\n  teacherRatingTags {\n    legacyId\n    "
                 "tagCount\n    tagName\n    id\n  }\n}\n\nfragment NameLink_teacher on Teacher {\n  "
                 "isProfCurrentUser\n  legacyId\n  lastName\n}\n\nfragment TeacherFeedback_teacher on Teacher {\n "
                 " numRatings\n  avgDifficulty\n  wouldTakeAgainPercent\n}\n\nfragment TeacherDepartment_teacher "
                 "on Teacher {\n  department\n  school {\n    legacyId\n    name\n    id\n  }\n}\n\nfragment "
                 "TeacherBookmark_teacher on Teacher {\n  id\n  isSaved\n}\n\nfragment NumRatingsLink_teacher on "
                 "Teacher {\n  numRatings\n  ...RateTeacherLink_teacher\n}\n\nfragment "
                 "RatingDistributionChart_ratingsDistribution on ratingsDistribution {\n  r1\n  r2\n  r3\n  r4\n  "
                 "r5\n}\n\nfragment HeaderDescription_teacher on Teacher {\n  id\n  firstName\n  lastName\n  "
                 "department\n  school {\n    legacyId\n    name\n    id\n  }\n  ...TeacherTitles_teacher\n  "
                 "...TeacherBookmark_teacher\n}\n\nfragment HeaderRateButton_teacher on Teacher {\n  "
                 "...RateTeacherLink_teacher\n}\n\nfragment TeacherTitles_teacher on Teacher {\n  department\n  "
                 "school {\n    legacyId\n    name\n    id\n  }\n}\n",
        "variables": {"id": "VGVhY2hlci0yMTk2"}
    }

    RATINGS_QUERY_PAGINATION = {
        "query": "query RatingsListQuery(  $count: Int!  $id: ID!  $courseFilter: String  $cursor: String) {  node("
                 "id: $id) {    __typename    ... on Teacher {      ...RatingsList_teacher_4pguUW    }    id  "
                 "}}fragment RatingsList_teacher_4pguUW on Teacher {  id  legacyId  lastName  numRatings  school {    "
                 "id    legacyId    name    city    state    avgRating    numRatings  }  ...Rating_teacher  "
                 "...NoRatingsArea_teacher  ratings(first: $count, after: $cursor, courseFilter: $courseFilter) {    "
                 "edges {      cursor      node {        ...Rating_rating        id        __typename      }    }    "
                 "pageInfo {      hasNextPage      endCursor    }  }}fragment Rating_teacher on Teacher {  "
                 "...RatingFooter_teacher  ...RatingSuperHeader_teacher  ...ProfessorNoteSection_teacher}fragment "
                 "NoRatingsArea_teacher on Teacher {  lastName  ...RateTeacherLink_teacher}fragment Rating_rating on "
                 "Rating {  comment  flagStatus  createdByUser  teacherNote {    id  }  ...RatingHeader_rating  "
                 "...RatingSuperHeader_rating  ...RatingValues_rating  ...CourseMeta_rating  ...RatingTags_rating  "
                 "...RatingFooter_rating  ...ProfessorNoteSection_rating}fragment RatingHeader_rating on Rating {  "
                 "date  class  helpfulRating  clarityRating  isForOnlineClass}fragment RatingSuperHeader_rating on "
                 "Rating {  legacyId}fragment RatingValues_rating on Rating {  helpfulRating  clarityRating  "
                 "difficultyRating}fragment CourseMeta_rating on Rating {  attendanceMandatory  wouldTakeAgain  grade "
                 " textbookUse  isForOnlineClass  isForCredit}fragment RatingTags_rating on Rating {  "
                 "ratingTags}fragment RatingFooter_rating on Rating {  id  comment  adminReviewedAt  flagStatus  "
                 "legacyId  thumbsUpTotal  thumbsDownTotal  thumbs {    userId    thumbsUp    thumbsDown    id  }  "
                 "teacherNote {    id  }}fragment ProfessorNoteSection_rating on Rating {  teacherNote {    "
                 "...ProfessorNote_note    id  }  ...ProfessorNoteEditor_rating}fragment ProfessorNote_note on "
                 "TeacherNotes {  comment  ...ProfessorNoteHeader_note  ...ProfessorNoteFooter_note}fragment "
                 "ProfessorNoteEditor_rating on Rating {  id  legacyId  class  teacherNote {    id    teacherId    "
                 "comment  }}fragment ProfessorNoteHeader_note on TeacherNotes {  createdAt  updatedAt}fragment "
                 "ProfessorNoteFooter_note on TeacherNotes {  legacyId  flagStatus}fragment RateTeacherLink_teacher "
                 "on Teacher {  legacyId  numRatings  lockStatus}fragment RatingFooter_teacher on Teacher {  id  "
                 "legacyId  lockStatus  isProfCurrentUser}fragment RatingSuperHeader_teacher on Teacher {  firstName  "
                 "lastName  legacyId  school {    name    id  }}fragment ProfessorNoteSection_teacher on Teacher {  "
                 "...ProfessorNote_teacher  ...ProfessorNoteEditor_teacher}fragment ProfessorNote_teacher on Teacher "
                 "{  ...ProfessorNoteHeader_teacher  ...ProfessorNoteFooter_teacher}fragment "
                 "ProfessorNoteEditor_teacher on Teacher {  id}fragment ProfessorNoteHeader_teacher on Teacher {  "
                 "lastName}fragment ProfessorNoteFooter_teacher on Teacher {  legacyId  isProfCurrentUser}",

        "variables": {"count": 10,
                      "id": "VGVhY2hlci0yMTk2",
                      "courseFilter": None,
                      "cursor": "YXJyYXljb25uZWN0aW9uOjE5"}
    }



    HEADERS = {
        'Authorization': 'Basic dGVzdDp0ZXN0',
        'Referer': 'https://www.ratemyprofessors.com/search/teachers?query=*&sid=1074',
        'Content-Type': 'application/json'
    }



    def __init__(self) -> None:
        self.data_dict, self.crawled_ratings, self.crawled_profs, self.file_open = dict(), set(), set(), False
        file = open("./settings/settings.json", "r")
        project_settings = json.load(file)
        file.close()
        self.thread_num = project_settings["thread_num"]
        self.output_path = project_settings["output_path"]
        self.school_ids_path = project_settings["school_ids_path"]
        self.id_col = project_settings["school_ids_column_name"]
        self.csv_headers = project_settings["csv_file_headers"]
        self.allow_duplicates = project_settings["allow_duplicates"]
        self.file_limit_rows = project_settings["file_limit_rows"]
        self.schools_picked = []
        self.file_number = 1
        self.counter = 0
        self.date_ = date.today()

   

    def scrape(self, school_ids: list) -> None:
        """Pick a school id from a list of school ids and request professor information"""
        thread, crawled_schools = threading.current_thread().name, set()
        logging.info(f"{thread} initialized. Proceeding to scrape data...")
        while len(school_ids):
            school_id = random.choice(school_ids)
            if school_id in self.schools_picked:continue
            progress_log = "{} Crawled Schools: {} || Queued Schools: {} || Professors found: {}"
            logging.info(progress_log.format(thread, len(crawled_schools), len(school_ids), len(self.crawled_profs)))
            self.schools_picked.append(school_id)
            self.TEACHERS_QUERY_INIT["variables"]["query"]["schoolID"] = school_id
            self.TEACHERS_QUERY_INIT["variables"]["schoolID"] = school_id
            query = json.dumps(self.TEACHERS_QUERY_INIT)
            while query: 
                try:query = self.fetch_professors_json_data_from_rmp(query, school_id)   
                except Exception as e:logging.info(e)
            school_ids.remove(school_id)
            crawled_schools.add(school_id)

    


    def fetch_professors_json_data_from_rmp(self, query, school_id) -> str:
        """Fetch professors json data from a given school id """
        response = requests.post(self.URL, data=query, headers=self.HEADERS)
        if  response.status_code == 200:
            json_data = json.loads(response.content)
            try:has_next_page = json_data["data"]["search"]["teachers"]["pageInfo"]["hasNextPage"]
            except:has_next_page = False
            self.extract_teacher_info_from_dict(json_data["data"])
        else:logging.info(f"Error fetching professors json: {response.status_code}")
        if  has_next_page:
            end_cursor = json_data["data"]["search"]["teachers"]["pageInfo"]["endCursor"]
            self.TEACHERS_QUERY_PAGINATION["variables"]["cursor"] = end_cursor
            self.TEACHERS_QUERY_PAGINATION["variables"]["query"]["schoolID"] = school_id
            query = json.dumps(self.TEACHERS_QUERY_PAGINATION)
            return query
        else:return ""
        

    
    def extract_teacher_info_from_dict(self, json_data: dict) -> None:
        """Extract professor bio information from a dictionary"""
        teacher_id_set = set()
        for teacher in json_data["search"]["teachers"]["edges"]:
            first_name, last_name = teacher["node"]["firstName"], teacher["node"]["lastName"]
            department, school = teacher["node"]["department"], teacher["node"]["school"]["name"]
            teacher_id, num_ratings = teacher["node"]["id"], teacher["node"]["numRatings"]
            self.data_dict[teacher_id] = {"name":f"{first_name} {last_name}", "dept":department,
                                          "school":school, "num_ratings":num_ratings}
            teacher_id_set.add(teacher_id)
        [self.fetch_teacher_ratings_from_rmp(id_) for id_ in teacher_id_set if not teacher_id in self.crawled_profs]
    


    def fetch_teacher_ratings_from_rmp(self, teacher_id) -> None:
        """Fetch ratings json data from a given teacher id """
        self.RATINGS_QUERY_INIT["variables"]["id"], ratings_set = teacher_id, set()
        query = json.dumps(self.RATINGS_QUERY_INIT)
        while True:
            try:
                response = requests.post(self.URL, data=query, headers=self.HEADERS)
                if  response.status_code != 200:
                    logging.info(f"Error fetching teacher ratings: {response.status_code}")
                    continue
                end_cursor = self.extract_ratings_slugs(json.loads(response.content), ratings_set)
                if  end_cursor:
                    self.RATINGS_QUERY_PAGINATION["variables"]["cursor"] = end_cursor
                    query = json.dumps(self.RATINGS_QUERY_PAGINATION)
                else:break
            except Exception as e:logging.info(e)
        if  teacher_id not in self.crawled_profs:
            self.data_dict[teacher_id]["reviews"] = ratings_set
            self.data_dict_handler(self.data_dict, teacher_id)
            self.crawled_profs.add(teacher_id)
    


    @staticmethod
    def extract_ratings_slugs(json_data, ratings_set:set) -> str:
        """Extract rating slugs from json"""
        try:end_cursor = json_data["data"]["node"]["ratings"]["pageInfo"]["endCursor"]
        except:end_cursor = ""
        if json_data["data"]["node"]:
            try:
                ratings = json_data["data"]["node"]["ratings"]["edges"]
                for rating in ratings:
                    rating_id, rating_value = rating["node"]["id"], rating["node"]["clarityRating"]
                    comment, course = rating["node"]["comment"], rating["node"]["class"] 
                    stripped_comment = ''.join(str(comment).splitlines())
                    ratings_set.add((rating_id, rating_value, course, stripped_comment))
            except Exception as e:logging.info(e)
        return end_cursor



    def data_dict_handler(self, data_dict: dict, key) -> None:
        """Unpack data from dictionary and save to csv file"""
        teacher, dept, school = data_dict[key]["name"], data_dict[key]["dept"], data_dict[key]["school"]
        len_ratings, master_list, thread_name= len(data_dict[key]["reviews"]), [], threading.current_thread().name
        for review in data_dict[key]["reviews"]:
            rating_id, rating_value, course, comment = review
            if not self.allow_duplicates and rating_id in self.crawled_ratings:continue
            fields = [f'{school} - {teacher} {course}', f'{course} {dept}', rating_value, comment, rating_id]
            master_list.append(fields)
            self.crawled_ratings.add(rating_id)
            len_ratings -= 1
            self.counter += 1
        logging.info(f"{thread_name} Rejected Duplicates: {len_ratings} || Non-duplicated Data: {len(self.crawled_ratings)}")
        while self.file_open:pass
        if self.counter >= self.file_limit_rows:
            self.file_number += 1
            self.counter = 0
        self.append_to_csv(f"{self.output_path}rmp_scraped_data_{self.date_}({self.file_number}).csv", master_list)
    



    def append_to_csv(self, directory, data: list) -> None:
        """Create csv file if it doesn't exists and append data"""
        self.file_open = True
        if not os.path.exists(self.output_path):os.makedirs(self.output_path)
        if not os.path.isfile(directory):
            with open(directory, "w",  newline='\n', encoding="utf-8") as file:
                writer = csv.writer(file, delimiter=",")
                writer.writerow(self.csv_headers)
                file.close()
        if len(data):
            with open(directory, "a", newline="\n", encoding="utf-8") as file:
                writer =  csv.writer(file, delimiter=",")
                [writer.writerow(row) for row in data]
                file.close()
        self.file_open = False



    def run(self) -> None:
        """Initialize threads"""
        school_ids = pandas.read_csv(self.school_ids_path)[self.id_col].to_list()
        [threading.Thread(target=self.scrape, args=(school_ids, )).start() for _ in range(self.thread_num)]



if __name__ == "__main__":                    
    scraper = RMPScraper()
    scraper.run()
import nltk
from nltk.tokenize import RegexpTokenizer
import pickle
import utils

ne_map = {
    "0": "O",
    "1": "DEGREE",
    "2": "MAJOR",
    "3": "UNIVERSITY",
    "4": "SCHOOL",
    "5": "TIMESTART",
    "6": "TIMEEND",

}


tokenizer = RegexpTokenizer(r'\w+')
#data = ["Ph. D. in Computer Science, Rutgers University-New Brunswick New Brunswick, NJ, 2003 to 2010", "Master of Science in Computer Science, California State University Hayward, CA, 2012 ", "M.Tech in Computer Science and Engineering, Indian Institute of Technology, 2010", "B.Tech in Computer Science and Engineering, Calicut University Calicut, Kerala", "Master of Science in Software Engineering, SAN JOSE STATE UNIVERSITY, San Jose, CA, August 2017 to August 2019", "Bachelor of Engineering in Electronics Engineering, UNIVERSITY OF PUNE Pune, Maharashtra, July 2008 to July 2012", "MS in Computer Science, San Jose State University San Jose, CA, August 2016 to May 2018", "Bachelor's of Engineering in Computer Engineering, University of Mumbai Mumbai, Maharashtra, 2009 to 2013", "Computer Software Engineering in San Jose State University, August 2017 to Present", "Undergrad (ECE) in GITAM University, Sri Chaitanya College, ", "B.E. in Instrumentation and Control in Instrumentation and Control, University of Pune, June 2007 to May 2011", "M.S. in Software Engineering San Jose State University August 2017 to Present", "B.E. in Computer Engineering Gujarat Technological University July 2011 to May 2015", "MS in Computer Science and Engineering Santa Clara University September 2015 to June 2017", "BE in Computer Science and Engineering Anna University Chennai, Tamil Nadu September 2008 to April 20121", "B.S. in Computer Science University of California San Diego San Diego, CA September 2012 to March 2016", "Computer Engineering Florida International University 2015 to 2017", "BS in Computer Science Hunan University of Commerce 2009 to 2014", "M.S in Technology Management in Technology Management University of Illinois Urbana-Champaign, IL ", "B.E in Computer Science and Engineering in Computer Science and Engineering Visveswaraiah Technological University Bengaluru, Karnataka", "MS in Computer Science University of Southern California Los Angeles, CA January 2016 to December 2017", "Master of Science in Computer Science in Computer Science Maharaja College for Women Perundurai, Tamil Nadu May 2007", "Bachelor of Science in Computer Science in Computer Science Vellalar College for Women Erode, Tamil Nadu January 2005", "Master of Science in Computer Science San Jose State University San Jose, CA December 2017", "Bachelor of Technology in Computer Science and Engineering Mahatma Gandhi University May 2011", "Master of Science in Financial Engineering in Financial Engineering University of Michigan Ann Arbor, MI December 2012", "BS in Information and Computing Science in National Beijing Jiaotong University Beijing, CN June 2011", "Master of Science in Software Engineering International Technological University San Jose, CA May 2015 to December 2016", "Bachelors of Technology in Information Technology Harcourt Butler Technological Institute Kanpur, Uttar Pradesh August 2007 to June 2011", "Master of Science in Computer Software Engineering San Jose State University San Jose, CA September 2016 to May 2018", "Bachelor of Technology in Computer Science and Engineering K L University Vijayawada, Andhra Pradesh September 2010 to May 2014"]
data = ["PhD in Electrical Engineering University of Illinois At Urbana-Champaign Urbana-Champaign, IL May 2006","BS in Electrical Engineering Tsinghua University 1992","BS in Engineering Mechanics Tsinghua University 1992","PhD in Engineering Mechanics Tsinghua University","Bachelor of Science in Mathematics in Mathematics UNIVERSITY OF MINNESOTA Minneapolis, MN 2002","MSc. in Applied Computer Science University of Ciego de Avila 2010 to 2012","Engineer in Computer Science University of Ciego de Avila 2005 to 2010","AS in Computer Science in Computer Science Foothill College Los Altos Hills, CA","AA in Computer Science Brown Mackie formally Southern Ohio College Fort Mitchell, KY","AA in Web Design and Multimedia Art Institute of Phoenix Phoenix, AZ 2001 to 2003","A.S. in Computer Science Santa Monica College","A.A.S. in Design and SQL Lake Area Technical Institute Watertown, SD May 2011","Diploma Miami Dade College Miami, FL","Associates in Computer Engineering Miami Lakes Educational Center Miami Lakes, FL","Computer Repair Certificate in Computer Repair BOCES Hempstead, NY January 1975 to June 1975","Associate in Computer Science Nassau Community College Garden City, NY June 1973","B.S. in Computer Engineering UW 2016","Bachelor of Science in Computer Science San Jose State University","Certification in Relational Database Systems and Design University of California Santa Cruz Extension Santa Cruz, CA","B.S. in Software Engineering IOWA STATE UNIVERSITY Ames, IA May 2016","UNIVERSITY OF BIRMINGHAM Birmingham 2015","B.S.E.E. in Electrical Engineering Mankato State 1988","B.S. in Business Mankato State University 1983","Computer Science, and Physics University of Minnesota June 1978 to July 1979","Biology Mankato State University September 1974 to December 1976","B.S. in Biology Mankato State University September 1970 to June 1974","Bachelor of Computer Science & Information Technology in Patan Multiple Campus Tribhuwan University Kathmandu, NP 2013","BS in Computer Science Mansfield Universty of Pennsylvania Mansfield, PA 2010 to 2013"]
iob_tagged = list()
print(ne_map)
for d in data:
    try:
        pos_tagged = nltk.pos_tag(tokenizer.tokenize(d))
        iob_tag = list()

        prev = ""
        print(d)
        for tag in pos_tagged:
            label = ne_map[str(input(tag))]
            if label != "O":
                if label == prev:
                    iob_label = "I-"+label
                else:
                    iob_label = "B-"+label
            else:
                iob_label = label
            prev = label
            iob_tag.append((tag[0],tag[1],iob_label))
        iob_tagged.append(iob_tag)
        print(iob_tag)
    except Exception as e:
        print(str(e))
        pass

utils.save_object(iob_tagged, "iob_tagged-2.txt")

#!/usr/bin/env python
# coding: utf-8

# I'll be using the usual libraries, Pandas, NumPy, Matplotlib. Nothing too fancy for my first publish.
# 
# I'd like to think of this as a personal journey into my own train of thoughts and what I observe from visualizing data that I haven't seen (well, I'll be honest, I did take a tiny peek through Excel, but it was for only a minute or two).
# 
# * Is this my best work yet? Probably not. I'm still improving.
# * Will there be Grammatical or Program related mistakes in this book? Probably Yes.
# * Could I have missed out on key observations? Probably Yes.
# * Will I go off on tangents at times? Yes.

# In[ ]:


# This Python 3 environment comes with many helpful analytics libraries installed
# It is defined by the kaggle/python docker image: https://github.com/kaggle/docker-python
# For example, here's several helpful packages to load in 

import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import matplotlib.pyplot as plt

# Input data files are available in the "../input/" directory.
# For example, running this (by clicking run or pressing Shift+Enter) will list the files in the input directory

import os
print(os.listdir("../input"))

# Any results you write to the current directory are saved as output.


# It's been years since I've written code professionally and the only naming structure that I learnt, was in Java and how we had to use a certain format for naming classes, variables, methods, etc.
# 
# Since I'm not on Java and I'm playing around with the data here, I will be creating variables similar to the data file name.
# 
# The data I'm looking at is Students Performance in Exams and how external factors like Parental level of Education, Preparation Tests, and Lunch factor into their performance.
# 
# The file contains headers which contain readable header names. Some of them have spaces or symbols on them, which I will be replacing with an underscore. This makes it easier for me to refer them as array indices, or as names on the DataFrame.

# In[ ]:


StudentsPerformance = pd.read_csv("../input/StudentsPerformance.csv")
StudentsPerformance.columns = StudentsPerformance.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('(', '').str.replace(')', '').str.replace('/','_')


# And since I am not visualizing the data on Excel or on any text editor outside the of the notebook, I visualize a portion of my data. I look at the headers and a small portion of how the data looks. The scores are mostly whole numbers, and not decimals so I won't have to worry about Float formatting

# In[ ]:


StudentsPerformance.head()


# I'll be honest, I did take a peek at the file in Excel before I started this off (Old habits die hard).
# 
# The scores are Math Score (math_score), Reading Score (reading_score), Writing Score (writing_score). Growing up, I didn't have Reading or Writing comprehension. It was all combined into one part called Grammar which was a part of our English subject.
# 
# Looking at this data, we have some interesting columns:
# * **gender**
#     * male and female. If my first hand experience in school and college taught me anything, it's that Female are quite competitive in terms of all-round Academics. I was a slightly above average joe, but nowhere close to the academic elite which was mostly comprised of female classmates and a few male classmates. Then college happened, and I started to notice that Math got more ambiguous, and my male classmates were finding more than one way to skin the cat, than their female counterparts. It'll be interesting to see if my past experiences still holds true
# * **race_ethnicity**
#     * This is an interesting column. There are five categories A through E. I believe that academic performance only relies on "how much of committed and honest work we put into it" and not how much of an RGB advantage we have over the competition.
# * **parental_level_of_education**
#     * Another interesting column. A student's drive is partly influenced by the how learned their parents are. This data only considers from some high school to a Master's Degree. A doctoral degree would've been nice, but this will do for now.
# * **lunch**
#     * I don't know what to make of this column, but there's Standard, and Free/Reduced. Unless there is documentation that outlines exactly what this column represents, I'll assume for this case that it's whether the student got a proper lunch or not. This one's pretty obvious: less food = less energy = less performance (but is that all?)
# * **test_preparation_course**
#     * Same scenario as **lunch**. I couldn't find documentation on this, but I'll assume that _None_ means the student didn't take any preparation courses, and _Completed_ means that they took it.
# 

# My analysis will be mostly based on how well each gender performs depending on external factors. So, for my convenience, I'll be spearating the data into a male group and female group.

# In[ ]:


StudentsPerformance_male = StudentsPerformance[StudentsPerformance.gender=="male"]
StudentsPerformance_female = StudentsPerformance[StudentsPerformance.gender=="female"]


# I'll simplify my analysis by using the common graphs. Pies for identifying the size of the groups, and bars for averages, and histograms for distributions

# In[ ]:


def graphs(score_type, suptitle, groupbyterm, kind):
    nrows = 2
    ncols = 3
    inches = 5
    fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=(ncols*inches,nrows*inches))
    fig.suptitle(suptitle)
    temp = StudentsPerformance[groupbyterm].value_counts().rename("")
    temp.plot.pie(ax=axes[0,0], title="# Students Overall", autopct="%.2f", legend=False)
    temp = StudentsPerformance_female[groupbyterm].value_counts().rename("")
    temp.plot.pie(ax=axes[0,1], title="# Female", autopct="%.2f", legend=False)
    temp = StudentsPerformance_male[groupbyterm].value_counts().rename("")
    temp.plot.pie(ax=axes[0,2], title="# Male", autopct="%.2f", legend=False)
    pd.concat([
        StudentsPerformance_female.groupby(groupbyterm)[score_type].mean().rename("Female"),
        StudentsPerformance_male.groupby(groupbyterm)[score_type].mean().rename("Male")], axis=1).plot(kind="bar", ax=axes[1,0], legend=True)
    axes[1,0].set_xlabel("")
    axes[1,0].legend([x.get_text().capitalize() for x in axes[1,0].legend().get_texts()])
    axes[1,0].set_xticklabels([x.get_text().capitalize() for x in axes[1,0].get_xticklabels()])
    StudentsPerformance_female.groupby(groupbyterm)[score_type].plot(kind=kind, ax=axes[1,1], legend=True, alpha=0.8, histtype="step")
    axes[1,1].set_xlabel("Female Scores")
    axes[1,1].set_ylabel("")
    axes[1,1].set_xticks(np.arange(0, 101, step=20))
    axes[1,1].set_yticks(np.arange(0, 101, step=20))
    axes[1,1].legend([x.get_text().capitalize() for x in axes[1,1].legend().get_texts()])
    StudentsPerformance_male.groupby(groupbyterm)[score_type].plot(kind=kind, ax=axes[1,2], legend=True, alpha=0.8, histtype="step")
    axes[1,2].set_xlabel("Male Scores")
    axes[1,2].set_ylabel("")
    axes[1,2].set_xticks(np.arange(0, 101, step=20))
    axes[1,2].set_yticks(np.arange(0, 101, step=20))
    axes[1,2].legend([x.get_text().capitalize() for x in axes[1,2].legend().get_texts()])
    return fig, axes


# **MATH**
# 
# We start off with Math and how each external factor played into each gender's performance.

# In[ ]:


ax=pd.concat([StudentsPerformance_female.groupby("gender")["math_score"].mean().rename("Female"), StudentsPerformance_male.groupby("gender")["math_score"].mean().rename("Male")]).plot(kind="barh", figsize=(16,4), title="Math Score Averages")
ax.set_yticklabels([y.get_text().capitalize() for y in ax.get_yticklabels()])
ax.set_ylabel("")


# When it comes to Math, males have outperformed their female counterparts regardless of external factors. But not by a large margin.
# 
# 

# In[ ]:


fig, axes = graphs("math_score","Math Scores by Parental Level of Education", "parental_level_of_education", "hist")


# **Parental Level of Education on a Student's math performance?**  
# 
# Very few parents hold a Bachelor's degree; fewer still, hold Master's degree. Because we have fewer samples of parents holding math degrees, it stands to show that the math scores for these students will be higher on average, as opposed to the other degrees. But looking at the more populated degrees, their scores also show variations, albeit not a lot, but variations nevertheless.
# 
# A more serious question to be asked is, Are the parents in general, to be blamed for not educating their kids enough at math? Or are their kids not providing sufficient importance to Math as opposed to reading and writing?
# 
# **My thoughts:** I'd like to think that parents with any degree should be able to teach their kids that Math isn't just solving for numbers, rather it's trying to understand why things are, the way they are, using facts. You don't need a shiny degree to be qualified to do that.

# In[ ]:


fig, axes = graphs("math_score","Math Scores by Race/Ethnicity", "race_ethnicity", "hist")


# **Race/Ethnicity on a sutdent's math performance?**
# 
# Shortest population in Race/Ethnic group A. And in terms of performance, they are still at the lowest on average.
# Most dense population in Race/Ethnic group C. In terms of performance, they're average.
# 
# What are Race/Ethnic Groups D and E, doing so good that the other groups can learn from?
# Also why does group C have the largest count of average-jane math performers? Sure, the boys in group C also have the highest count of average-joe math performers, but not as significant as their female counterparts. Are they not paying as much attention to math as other academics?
# 
# **My thoughts:** I'll say it again, my opinion on Math is that it's purely analytical. So I'd like to think race/ethnicity shouldn't matter when it comes to math. But the numbers seem to have a different take on it. 

# In[ ]:


fig, axes = graphs("math_score","Math Scores by Lunch", "lunch", "hist")


# **Lunch on a Student's math performance**
# 
# Following the averages, boys still outperform the girls at math regardless of lunch. Almost two-thirds of the students had a standard lunch. It's good to know that these students didn't sacrifice their stomachs for math scores.
# 
# **My thoughts:** Solving a problem is more easier when we're focused on it rather than not. So it goes without saying that having a standard lunch does improve our chances of better math performance. This is a good thing. Over here, students get so caught up in the exam fever, that they end up sacrificing food, recreation, even sleep time just so they could do well in the exams.

# In[ ]:


fig, axes = graphs("math_score","Math Scores by Test Preparation Course", "test_preparation_course", "hist")


# **Test Preparation course on the Student's math performance**
# 
# Going off of the numbers in the graphs, Only a third of the students are taking these courses seriously. And the ones that did take the courses aren't having a significant advantage at math. So should the Preparatory courses be cancelled? Looking at the smaller bounds, Students that took the preparatory course have higher baselines than the ones that didn't. So it's probably good to keep them going.
# 
# **My thoughts:** While only a third of the students took the Preparatory course (which is good), it's probably good to note why the rest didn't take it. What's causing these students to not take the courses? 

# **How to do well at math?**
# 
# Stating the obvious, Your performance in math shouldn't rely on your parents, or ethnic groups (though the numbers say otherwise). Even if it did, you can't change your RGB tones in order to improve your odds at exam. I guess I just found one of those examples of Correlation does not equal causation. 
# 
# It's about how you see the math. It's a question if you see it as a question, and can be one major problem if you see it as a problem. Also, have a standard breakfast/lunch, and just take the preparatory courses. That should be more than sufficient to improve your chances of performing better at math. 
# 
# **My thoughts**
# 
# Would've been great if there was a column which showed how much sleep each student got, the night before the exam. 
# 
# Throughout my school days I knew that 2+2 was always going to be 4, so I accepted it and never questioned why it was the way it was. This resulted in me memorizing each step of every equation that I came across without questioning it. 
# 
# It was only later on in my journey that I found that there was more to math than just numbers and calculations (The same can be said for my understanding of things in general). Had I known this fact earlier, I would've performed just a little better, ended up elsewhere in a butterfly effect, or worse never compiled this. 
# 
# I'll always believe that honest effort put into something we like, will yield a good result, if not great, or outstanding result. Math doesn't really require much effort if we're thinking analytically, but analytical thinking comes with continuous learning application of acquired learnings.
# 
# Did I go off on a tangent and fall into a bottomless pit of past memories, and nostalgia? YES.

# **READING**
# 
# Ah, reading. Back when I was a student, part of our English subject included grammar and comprehension. Although reading wasn't a test, trying to get the grammar right was just as much of a challenge as it was for writing.
# 
# Since we weren't put into any type of reading exams, my analysis here is only based on numbers and some ramblings from what I can remember from my days of being a student.

# In[ ]:


ax=pd.concat([StudentsPerformance_female.groupby("gender")["reading_score"].mean().rename("Female"), StudentsPerformance_male.groupby("gender")["reading_score"].mean().rename("Male")]).plot(kind="barh", figsize=(16,4), title="Reading Score Averages")
ax.set_yticklabels([y.get_text().capitalize() for y in ax.get_yticklabels()])
ax.set_ylabel("")


# Starting off with the averages, girls, you've outperformed the boys when it come to reading.
# 
# Girls on average, have 70ish scores on reading, regardless of their parental degrees (although there's something to be said for parents holding associate degrees). But anyway, they're doing it right.
# 
# Most of my language was taught by cartoons, National Geographic, and the likes.

# In[ ]:


fig, axes = graphs("reading_score","Reading Scores by Parental Level of Education", "parental_level_of_education", "hist")


# **Parental level of Education on the Student's reading skills**
# 
# Most students are above average when it comes to reading, which is a good thing. Children of parents who hold masters degree (a small population) fare better at reading than the others. Is it because these kids have access to something that the other kids don't? Regardless, these parents are doing something right, that the other parents could maybe learn from.
# 
# Parents who hold a high school degree have daughters who fare just as well as the daughters of parents who hold a master's degree. The same holds for the boys as well. This clearly shows that a student's reading skill is almost independent of their parental level of education.
# 
# **My thoughts:** Reading is probably one of those activities that can be done as a leisure activity. Sure, you can solve math at free time, but it isn't as good as reading book, or just snippets of text, and comprehending read text. So, to the parents, start encouraging your kids to read from an early age. Not just read, but to imagine them.

# In[ ]:


fig, axes = graphs("reading_score","Reading Scores by Race/Ethnicity", "race_ethnicity", "hist")


# **Race/Ethnicity on a Child's reading skills**
# 
# Group C has the highest population, so it goes without saying that students in this group are on the average here.
# 
# Groups D and E, you are faring better at reading than the other groups. So whatever it is you're doing, keep at it plus a little extra so you can keep improving. It's good if you're okay and improving as compared to being really good and have no improvement.
# 
# Also there's a good population of girls that are exceptional readers as opposed to the boys. Why is it that there are so few (almost non-existent) boys that are exceptional readers? Numbers caught your brain?
# 
# **My thoughts:** Race/Ethnicity shouldn't be a factor in reading. Even though the numbers say otherwise, it's not right to say I'm bad at reading because I belong to a certain race/ethnic group. So if you want to get better at reading, start reading. Readable content is everywher (Most of it's free on the internet, or just pick up the newspaper, and maybe a dictionary for those rarely used words).

# In[ ]:


fig, axes = graphs("reading_score","Reading Scores by Lunch", "lunch", "hist")


# **Lunch on a Student's reading performance**
# 
# Student's did have a standard lunch. So they've performed well. Those that had a free or reduced lunch performed reasonably well. Since reading and comprehension is part of our daily lives, Lunch is almost negligible factor in reading. But don't go by numbers and take a reading exam on an empty stomach though.

# In[ ]:


fig, axes = graphs("reading_score","Reading Scores by Test Preparation Course", "test_preparation_course", "hist")


# **Test Preparation Course on a Student's reading performance**
# 
# Only a third of the students took a test preparation course. But no information is mentioned as to whether it was for all subjects or just some.
# 
# That being said, Those who completed their tests fared better than those who didn't. There's a noticeable shift in the curve that indicates this, and like mentioned earlier, reading improves reading.
# 
# But this brings me back to my question from Math. Why are two-thirds of the students not taking the preparatory course? Is the institution not encouraging their students to take the exam? or are the students finding the exam not so worthwhile?

# **How to do well at reading exam?**
# 
# Reading, having a good meal, and a sound sleep, improves your chances at a reading test. But just because you scored the highest marks possible doesn't mean you've reached the top of the mountain. While reading is almost like riding a bike (hard to forget once learnt), it's a good activity for the brain and the imagination. I, for one, can't find the focus to read a novel (sounds hypocritical), but I do love reading a short story, a good news article, and maybe in the future, a novel.
# 
# **My thoughts**
# 
# With reading being a favored activity before sleeping, it'd be interesting to see if literature has any influence on sleep patterns.
# 
# Does reading on just the subject the previous day help improve your reading performance or does reading something besides the subject help improve your reading performance? I read an interesting article the other day on how reading something interesting helps form stronger neural pathways in the brains)
# 
# I'd like to think that reading helps develop character; that, having something good to read and being able to comprehend read text (or imagine the story take place in our minds through the author's words), brings a kind of intrigue, that's good for the brain, which, along with other factors help us become better people. (Not saying that we'd become cannibalistic killers if we read Hannibal)

# **WRITING**
# 
# I'm not even sure how many miles I've written all my life. But I'm very sure that it's less than my ancestors. With everything going digital these days, there's a kind of fear in the back of my head, that human evolution will eventually lead to us forgetting how to write
# 
# All our exams were written content, but there wasn't an exam dedicated for our writing abilities. English as an exam subject did contain essay writing or answers based on a given paragraph, but I find these higher exams like SATs, GMATs, IELTS, or TOEFL or the likes to be a good medium to gauge our writing skills.

# In[ ]:


ax=pd.concat([StudentsPerformance_female.groupby("gender")["writing_score"].mean().rename("Female"), StudentsPerformance_male.groupby("gender")["writing_score"].mean().rename("Male")]).plot(kind="barh", figsize=(16,4), title="Writing Score Averages")
ax.set_yticklabels([y.get_text().capitalize() for y in ax.get_yticklabels()])
ax.set_ylabel("")


# Not much to say on the averages, besides,  all students performing well above average, and girls outperforming the boys by a good margin

# In[ ]:


fig, axes = graphs("writing_score","Writing Scores by Parental Level of Education", "parental_level_of_education", "hist")


# **Parental Education on a Student's writing performance**
# 
# Kids do better at writing when their parents have higher degrees. But I'd like to think that this is one of those cases where corelation does not equal causation. Much like reading, anyone can be taught to write, and with practice comprehend read text and reproduce them back as meaningful answers or ideas.
# 
# Parents with Master's degree, although a small population, have kids that fare better at writing than the parents holding other degrees. Except for parents with high school degrees, there's a good amount of girls that are exceptional writers as opposed to their male counterparts.
# 
# Why do kids with Parents holding master's degree score better at reading and writing as opposed to parents holding other degrees?
# Is there any difference in literature that the kids are exposed to, based on parental level of education?
# 
# **My thoughts:** Is it possible that there's some sort of socio-economic status held by parents holding higher degrees, that lead them to blend with more of their kind (something like a pack) that improves reading/writing abilities for their kids? (Holy crap that's a lot of words)

# In[ ]:


fig, axes = graphs("writing_score","Writing Scores by Race/Ethnicity", "race_ethnicity", "hist")


# **Race/Ethnicity on the Student's writing performance**
# 
# Groups D and E rank highest in average writing performance, while having an average population density similar to Group B. (Group A and C not considered to due the visibly large variation)
# 
# When it comes to writing, the best performing females mostly belong to Group C, D and E. It's worth noting that a fair amount of them are exceptional writers.
# Best performing males belong to Groups D and E although there's very few exceptional writers here. Group C shows some hope here with exceptional writers, but that's about it.
# One thing's for certain, Race/Ethnicity is negligible when it comes to the outstanding writers in general.
# 
# **My thoughts:** Can't blame race/ethnicity if you're not able to write well. Writing improves writing. So get that pen and paper and start comprehending.

# In[ ]:


fig, axes = graphs("writing_score","Writing Scores by Lunch", "lunch", "hist")


# **Lunch on the Student's writing performance**
# 
# Two-thirds had a standard lunch. And they did perform better than students that had a free/reduced lunch. Why did these student's have a free/reduced lunch? Insufficient data to dig into.
# 
# Looking at the lower bounds:
# * Lowest performance for girls that had a free/reduced lunch is somewhere in the 10s.
# * Lowest performance for girls that had a standard lunch is at least a 30.
# * While there is a smaller margin, the same can be said for boys as well.

# In[ ]:


fig, axes = graphs("writing_score","Writing Scores by Test Preparation Course", "test_preparation_course", "hist")


# **Preparation Course on a Student's writing performance**
# 
# It might not have been true for Math, but completing the Test Preparaion Course does help improve reading and writing performance.
# 
# Only a third may have completed the preparation course but look at those numbers; there's a very noticeable difference in the baselines
# 
# Girls, you may be good at writing regardless of whether you complete the course or not (just look at the higher bounds), but it wouldn't hurt to take the preparatory course anyway.
# Boys, just take the course, your performance noticeably improves and the numbers above show it.
# 
# **My thoughts:** Reading and Writing are mutually dependent. So take the prepartory course. If it doesn't help your writing (I'd be surprised if a writing prep didn't help writing), it'll help your reading.

# **How to do well at writing exam?**
# 
# Read well, Eat well, Maybe get sufficient sleep the day before the exam, and take the preparation course, and you should be good to go for the writing test
# 
# **My thoughts**
# 
# It doesn't matter if you're a kid or an adult, you'll need to write. If not write paragraphs, poems, or essays, you'll need it for scribbling your signature on documents. It won't be long before 0s and 1s take over the signature too, but until then, the pen will remain mightier than the sword (and computers, for now)
# 
# Like mentioned earlier. Reading and writing are mutually dependent. One improves the other. So if you want to improve your reading, you'd do well by writing; and if you want to improve your writing, you might as well start reading.

# **FINAL THOUGHTS**
# 
# Coming to the scores, it goes without saying that one can fare better at exams if he/she prepares for it. But preparation alone isn't enough. You'd have to ensure your brain stays healthy and part of that can be achieved by having a good meal, proper rest
# 
# **My thoughts after compiling this**
# 
# If you've come this far, I'd like to thank you for spending the time on what I can only consider as a guy going off the rails on a dataset. It only took me like two long weeks, several hours, and lots of mistakes. There's room for me to improve, but considering this is my first data analysis on a notebook, I'm quite happy with the results
# 
# I'm no stranger to writing code. But when it comes to consulting, it becomes more important to getting the idea or the story across than it is preparing it. Most of my hours when preparing reports, are spent trying to find the right type of visualization to show why something is the way it is (and this is using Excel and no little to no programming whatsoever). 
# 
# It gets even more complicated if you're the one preparing you're not the one that's presenting it. Sure, there's subjects and degrees that teach you when to use what visualization, but how do you convey that to someone who's gotten rusty at it or hasn't taken the same subjects as you have? Do you spend time explaining the backstory? or Do you end up redesigning what was a good visualization, by trying to dumb it down, only to end up convoluting it further?
# 
# Anyway, having worked extensively with Excel and it's visualizations, it's nice to know that this is just as flexible as Excel and the likes. I might be more comfortable with Excel since most of my data is moderately sized or is in one large table, but it's nice to know that if data gets out of control, I can rely on some well written variables and operations to get things done.
# 
# How quickly will I start off with the next notebook? Probably not in the next few minutes (at least). I'm still intimidated with super large datasets, not because they're large in size, but because they're probably more complex than I had imagined or not within my knowledge boundaries. To quote Timothy Ferriss in his book "The 4-Hour Workweek"
# >"Being able to quit things that don't work is integral to being a winner. Going into a project or job without defining when worthwhile becomes wasteful is like going into a casino without a cap on what you will gamble: dangerous and foolish."
# 
# Tips on the notebook, analyses, codes, comments or criticism, or just thoughts in general? Do let me know.
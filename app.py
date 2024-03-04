import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns

import urlextract
import wordcloud
import collections
import emoji
import pandas as pd

import re





#HELPER.PY
def fetch_stats(selected_user, df):
    if selected_user != 'OverAll':
        df = df[df['user'] == selected_user]

    total_messages = df.shape[0]
    total_words = len(' '.join(df['message']).split())

    media_cnt = 0
    media = 'Media omitted'
    for message in df['message']:
        if media in message:
            media_cnt +=  1

    extractor = urlextract.URLExtract()
    links = []
    for link in df['message']:
        links.extend(extractor.find_urls(link))
    for link in links:
        if link[0:4] != 'http':
            links.remove(link)

    return total_messages, total_words, media_cnt, len(links)


def most_busy_users(df):
    x = df['user'].value_counts().head()
    df = round((df['user'].value_counts()/df.shape[0])*100, 2).reset_index().rename(columns={'user': 'Name', 'count': 'Percent'})
    
    return x, df


def create_word_cloud(selected_user, df):
    if selected_user != 'OverAll':
        df = df[df['user'] == selected_user]
    
    df = df[df['user'] != 'group_notification']
    temp = df[df['message'] != '<Media omitted>\n']
    temp['message'] = df['message'].apply(lambda x: emoji.demojize(x))

    f = open('stop_hinglish.txt', 'r')
    stop_words = f.read()
    special_symbols = ['!', '&', '#', ',', '*', '@', '$', '%', '-', '=', '+', '^', '_', '-', '–']

    words = []
    for msg in temp['message']:
        for word in msg.lower().split():
            if word not in stop_words:
                if word.isdigit() or word[0:4] == 'http' or word[0:1] == ':' or word in special_symbols:
                    continue
                elif word == 'ﷺ':
                        words.append('Rasulallah_SAW')
                elif word == 'اللّٰهَ' or word == 'اللّٰهِ':
                    words.append('Allah')
                elif word == 'الَّذِيۡنَ' or word == 'وَ' or word == 'مِّنۡ' or word == 'اِنَّ':
                    words.append('Quran_Ayah')
                else:
                    if len(word.split(':')) > 1:
                        words.append(word.split(':')[0])
                    else:
                        words.append(word)
        
    wc = wordcloud.WordCloud(width=500, height=500, min_font_size=10, background_color='white')
    df_for_wc = wc.generate(' '.join(words))
    
    return df_for_wc


def most_common_words(selected_user, df):
    if selected_user != 'OverAll':
        df = df[df['user'] == selected_user]

    temp = df[df['user'] != 'group_notification']
    temp = temp[temp['message'] != '<Media omitted>\n']
    temp['message'] = temp['message'].apply(lambda x: emoji.demojize(x))

    f = open('stop_hinglish.txt', 'r')
    stop_words = f.read()
    special_symbols = ['!', '&', '#', ',', '*', '@', '$', '%', '–', '=', '+', '^', '_']

    words = []
    for msg in temp['message']:
        for word in msg.lower().split():
            if word not in stop_words:
                if word.isdigit() or word[0:4] == 'http' or word[0:1] == ':' or word in special_symbols:
                    continue
                elif word == 'ﷺ' or word == 'rasoolallah':
                        words.append('Rasulallah_SAW')
                elif word == 'اللّٰهَ' or word == 'اللّٰهِ':
                    words.append('Allah')
                elif word == 'الَّذِيۡنَ' or word == 'وَ' or word == 'مِّنۡ' or word == 'اِنَّ':
                    words.append('Quran_Ayah')
                else:
                    if len(word.split(':')) > 1:
                        words.append(word.split(':')[0])
                    else:
                        words.append(word)

    new_df = pd.DataFrame(collections.Counter(words).most_common(20)).rename(columns={0: 'word', 1: 'count'})
    new_df = new_df[new_df['word'] != "*"].head(20)
    
    return new_df


def monthly_activity(user, df):
    if user != 'OverAll':
        df = df[df['user'] == user]

    df = df.groupby(['year', 'num_month', 'month']).count()['message'].reset_index()

    timel = []
    for i in range(df.shape[0]):
        timel.append(df['month'][i] + '-' + str(df['year'][i]))

    df['time'] = timel 
        
    return df


def daily_activity(user, df):
    if user != 'OverAll':
        df = df[df['user'] == user]

    daily_timeline = df.groupby(['only_date']).count()['message'].reset_index()

    return daily_timeline


def week_activity_map(user, df):
    if user != 'OverAll':
        df = df[df['user'] == user]

    return df['day_name'].value_counts().reset_index().rename(columns={'count': 'message'})


def month_activity_map(user, df):
    if user != 'OverAll':
        df = df[df['user'] == user]

    return df['month'].value_counts().reset_index().rename(columns={'count': 'message'})


def most_busy_hour(user, df):
    if user != 'OverAll':
        df = df[df['user'] == user]

    return df.groupby(['text_hour']).count()['message'].reset_index().sort_values(['message'], ascending=False)


def activity_heatmap(user, df):
    if user != 'OverAll':
        df = df[df['user'] == user]

    activity_heatmap_df = df.pivot_table(index='day_name', columns='text_hour', values='message', aggfunc='count')

    return activity_heatmap_df







#PREPROCESSOR.PY
def preprocess(data):
    flag = 0
    for element in data[0:30].split():
        if element.lower() == 'am' or element.lower() == 'pm':
            flag = 1

    if flag == 1:
        pattern = '\d{1,2}/\d{1,2}/\d{2},\s\d{1,2}:\d{2}\s[APMapm]{2}\s-\s'
    else:
        pattern = '\d{1,2}/\d{1,2}/\d{2},\s\d{1,2}:\d{2}\s-\s'
        
    messages = re.split(pattern, data)
    dates = re.findall(pattern, data)

    messages = messages[2:]
    dates = dates[1:]

    time = []

    for i in range(len(dates)):
        time.append(dates[i].split()[2])
        dates[i] = " ".join(dates[i].split()[0:2])

    for i in range(len(dates)):
        if (time[i] == 'AM') and int(dates[i].split()[1].split(':')[0]) == 12:
            dates[i] = dates[i].split()[0].split(',')[0] + ' ' + '00' + ':'+dates[i].split()[1].split(':')[1]
        if (time[i] == 'PM') and int(dates[i].split()[1].split(':')[0]) != 12:
            dates[i] = dates[i].split()[0].split(',')[0] + ' ' + str(int(dates[i].split()[1].split(':')[0])+12)+':'+dates[i].split()[1].split(':')[1]
    
    df = pd.DataFrame({'user_message': messages, 'message_date': dates})

    df['message_date'] = pd.to_datetime(df['message_date'], format='mixed')

    df.rename(columns={'message_date': 'date'}, inplace=True)

    users = []
    text_messages = []

    for message in df['user_message']:
        entry = re.split('([\w\W]+?):\s', message)
        if entry[1:]:
            users.append(entry[1])
            text_messages.append(entry[2])
        else:
            users.append('group_notification')
            text_messages.append(entry[0])

    am_pm = {0: '12-AM', 1: '01-AM', 2: '02-AM', 3: '03-AM', 4: '04-AM', 5: '05-AM', 6: '06-AM', 7: '07-AM', 8: '08-AM', 9: '09-AM', 10: '10-AM', 11: '11-AM', 12: '12-PM', 13: '01-PM', 14: '02-PM', 15: '03-PM', 16: '04-PM', 17: '05-PM', 18: '06-PM', 19: '07-PM', 20: '08-PM', 21: '09-PM', 22: '10-PM', 23: '11-PM'}

    df['user'] = users
    df['message'] = text_messages
    df.drop(columns=['user_message'], inplace=True)

    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month_name()
    df['num_month'] = df['date'].dt.month
    df['day'] = df['date'].dt.day
    df['day_name'] = df['date'].dt.day_name()
    df['hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute
    hour_am_pm = []
    for i in df['hour']:
        hour_am_pm.append(am_pm[i])
    df['text_hour'] = hour_am_pm
    df['only_date'] = df['date'].dt.date

    df.drop(columns=['date'], inplace=True)

    return df






#APP.PY
# Set page configuration
st.set_page_config(page_title="WhatsApp Chat Analyzer", page_icon=":chart_with_upwards_trend:", layout="wide", initial_sidebar_state="expanded")

st.sidebar.title("WhatsApp Chat Analyzer")

def space():
    col1, col2, col3 = st.columns(3)
    with col1:
        st.write('                ')
    with col2:
        st.write('                ')
    with col3:
        st.write('                ')

uploaded_file = st.sidebar.file_uploader("Choose a file")
if uploaded_file is not None:
    # To read file as bytes:
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode('utf-8')
    
    df = preprocess(data)

    #fetch unique users
    user_list = df['user'].unique().tolist()
    to_remove = 'group_notification'
    if to_remove in user_list:
        user_list.remove(to_remove)
    user_list.sort()
    user_list.insert(0, 'OverAll')

    selected_user = st.sidebar.selectbox('Show Analysis for', user_list)

    if st.sidebar.button('Show Analysis'):

        st.title("Top Statistics")

        num_messages, num_words, media_cnt, total_links = fetch_stats(selected_user, df)

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.header('Total Messages')
            st.header(num_messages)
        with col2:
            st.header('Total No. Words')
            st.header(num_words)
        with col3:
            st.header('Total Media Shared')
            st.header(media_cnt)
        with col4:
            st.header('Total Links Shared')
            st.header(total_links)

        space()
        space()
        space()

        #Finding the Bussiest Users in the Group (GROUP LEVEL)
        if selected_user == 'OverAll':
            st.title('Most Busy Users')
            most_busy_ones, new_df = most_busy_users(df)

            fig, ax = plt.subplots()
            
            col1, col2 = st.columns(2)
            with col1:
                ax.barh(most_busy_ones.index, most_busy_ones.values, color='green')
                st.pyplot(fig)
            with col2:
                st.dataframe(new_df)
        
        space()
        space()
        space()

        #WordCloud
        if(selected_user != 'OverAll'):
            st.title("Word Cloud : " + selected_user)
        else:
            st.title('Word Cloud')
        df_wc = create_word_cloud(selected_user, df)
        fig, ax = plt.subplots()
        ax.imshow(df_wc)
        st.pyplot(fig)
        
        space()
        space()
        space()


        #Most_Common_Words
        if(selected_user != 'OverAll'):
            st.title("Most Common Words : " + selected_user)
        else:
            st.title('Most Common Words')
        most_common_df = most_common_words(selected_user, df)
        fig, ax = plt.subplots()
        ax.barh(most_common_df['word'], most_common_df['count'], color='green')
        st.pyplot(fig)

        space()
        space()
        space()

        # Monthly Activity
        if(selected_user != 'OverAll'):
            st.title("Monthly Activity : " + selected_user)
        else:
            st.title('Monthly Activity')
        monthly_activity_df = monthly_activity(selected_user, df)
        fig, ax = plt.subplots()
        ax.plot(monthly_activity_df['time'], monthly_activity_df['message'], color='green')
        plt.xticks(rotation=90)
        st.pyplot(fig)

        space()
        space()
        space()

        # Daily Activity
        if(selected_user != 'OverAll'):
            st.title("Daily Activity : " + selected_user)
        else:
            st.title("Daily Activity")
        daily_activity_df = daily_activity(selected_user, df)
        fig, ax = plt.subplots()
        ax.plot(daily_activity_df['only_date'], daily_activity_df['message'], color='green')
        plt.xticks(rotation=90)
        st.pyplot(fig)

        space()
        space()
        space()

        # Weekly Activity
        st.title("Activity Map")
        col1, col2 = st.columns(2)

        #Most Busy Day
        weekly_activity_df = week_activity_map(selected_user, df)
        with col1:
            if(selected_user != 'OverAll'):
                st.header('Most Busy Day : ' + selected_user)
            else:
                st.header('Most Busy Day')
            fig, ax = plt.subplots()
            ax.barh(weekly_activity_df['day_name'], weekly_activity_df['message'], color='green')
            st.pyplot(fig)

        #Most Busy Month
        month_activity_df = month_activity_map(selected_user, df)
        with col2:
            if(selected_user != 'OverAll'):
                st.header('Most Busy Month : ' + selected_user)
            else:
                st.header('Most Busy Month')
            fig, ax = plt.subplots()
            ax.barh(month_activity_df['month'], month_activity_df['message'], color='yellow')
            st.pyplot(fig)

        # Hour Wise
        col1, col2 = st.columns(2)

        modt_busy_hour_df = most_busy_hour(selected_user, df)

        #Most Busy Hour        
        with col1:
            if(selected_user != 'OverAll'):
                st.header('Most Busy Hour : ' + selected_user)
            else:
                st.header('Most Busy Hour')

            fig, ax = plt.subplots()
            ax.barh(modt_busy_hour_df['text_hour'], modt_busy_hour_df['message'], color='yellow')
            st.pyplot(fig)
        
        space()
        space()
        space()


        #Activity HeatMap
        activity_heatmap_df = activity_heatmap(selected_user, df)

        if(selected_user != 'OverAll'):
                st.header('Activity HeatMap : ' + selected_user)
        else:
            st.header('Activity HeatMap')

        fig, ax = plt.subplots()
        ax = sns.heatmap(activity_heatmap_df)
        ax.set_xlabel('Time', color='red', labelpad=15)
        ax.set_ylabel('Days', color='red', labelpad=10)


        st.pyplot(fig)

        

        


        

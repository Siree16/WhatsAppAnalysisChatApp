import streamlit as st
from streamlit_option_menu import option_menu
import preprocessor, helper
import matplotlib.pyplot as plt
import seaborn as sns

# Setting the style for the entire app
st.set_page_config(page_title="Whatsapp Chat Analyzer", layout="wide", page_icon="💬")

st.markdown(
    """
    <style>
    .main {
        background-color: #ffe4e1; /* Baby pink background */
        padding: 20px;
        border-radius: 10px;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #4CAF50;
    }
    .css-1d391kg {
        background-color: #add8e6; /* Baby blue sidebar */
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Sidebar configuration with option menu
with st.sidebar:
    selected_page = option_menu("📊 Whatsapp Chat Analyzer", ["Upload", "Top Statistics", "Timelines", "Activity Map", "Busiest Users", "WordCloud", "Common Words", "Emoji Analysis"],
                                icons=['upload', 'bar-chart', 'clock', 'map', 'people', 'cloud', 'book', 'emoji-smile'],
                                menu_icon="cast", default_index=0)

if selected_page == "Upload":
    uploaded_file = st.file_uploader("Choose a file")
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        data = bytes_data.decode("utf-8")
        df = preprocessor.preprocess(data)

        # Fetch unique users
        user_list = df['user'].unique().tolist()
        user_list.remove('group_notification')
        user_list.sort()
        user_list.insert(0, "Overall")

        selected_user = st.selectbox("Show analysis with respect to", user_list)

        if st.button("Show Analysis"):
            st.session_state['data'] = df
            st.session_state['user'] = selected_user
            st.session_state['uploaded'] = True
else:
    if 'uploaded' in st.session_state and st.session_state['uploaded']:
        df = st.session_state['data']
        selected_user = st.session_state['user']

        if selected_page == "Top Statistics":
            st.markdown("## Top Statistics")
            num_messages, words, num_media_messages, num_links = helper.fetch_stats(selected_user, df)
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Total Messages", num_messages)
            with col2:
                st.metric("Total Words", words)
            with col3:
                st.metric("Media Shared", num_media_messages)
            with col4:
                st.metric("Links Shared", num_links)

        elif selected_page == "Timelines":
            st.markdown("## Monthly Timeline")
            timeline = helper.monthly_timeline(selected_user, df)
            fig, ax = plt.subplots()
            ax.plot(timeline['time'], timeline['message'], color='green')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

            st.markdown("## Daily Timeline")
            daily_timeline = helper.daily_timeline(selected_user, df)
            fig, ax = plt.subplots()
            ax.plot(daily_timeline['only_date'], daily_timeline['message'], color='black')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

        elif selected_page == "Activity Map":
            st.markdown("## Activity Map")
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("### Most Busy Day")
                busy_day = helper.week_activity_map(selected_user, df)
                fig, ax = plt.subplots()
                ax.bar(busy_day.index, busy_day.values, color='purple')
                plt.xticks(rotation='vertical')
                st.pyplot(fig)

            with col2:
                st.markdown("### Most Busy Month")
                busy_month = helper.month_activity_map(selected_user, df)
                fig, ax = plt.subplots()
                ax.bar(busy_month.index, busy_month.values, color='orange')
                plt.xticks(rotation='vertical')
                st.pyplot(fig)

            st.markdown("## Weekly Activity Map")
            user_heatmap = helper.activity_heatmap(selected_user, df)
            fig, ax = plt.subplots()
            ax = sns.heatmap(user_heatmap, cmap='YlGnBu')
            st.pyplot(fig)

        elif selected_page == "Busiest Users":
            if selected_user == 'Overall':
                st.markdown("## Most Busy Users")
                x, new_df = helper.most_busy_users(df)
                fig, ax = plt.subplots()

                col1, col2 = st.columns(2)

                with col1:
                    ax.bar(x.index, x.values, color='red')
                    plt.xticks(rotation='vertical')
                    st.pyplot(fig)
                with col2:
                    st.dataframe(new_df)

        elif selected_page == "WordCloud":
            st.markdown("## Wordcloud")
            df_wc = helper.create_wordcloud(selected_user, df)
            fig, ax = plt.subplots()
            ax.imshow(df_wc)
            ax.axis('off')
            st.pyplot(fig)

        elif selected_page == "Common Words":
            st.markdown("## Most Common Words")
            most_common_df = helper.most_common_words(selected_user, df)
            fig, ax = plt.subplots()
            ax.barh(most_common_df[0], most_common_df[1], color='skyblue')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

        elif selected_page == "Emoji Analysis":
            st.markdown("## Emoji Analysis")
            emoji_df = helper.emoji_helper(selected_user, df)

            col1, col2 = st.columns(2)

            with col1:
                st.dataframe(emoji_df)
            with col2:
                fig, ax = plt.subplots()
                ax.pie(emoji_df[1].head(), labels=emoji_df[0].head(), autopct="%0.2f")
                st.pyplot(fig)
    else:
        st.warning("Please upload a file to analyze.")

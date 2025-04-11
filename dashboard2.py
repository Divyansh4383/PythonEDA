import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv(r"c:\Users\VICTUS\Desktop\EXCEL\33_Constituency_Wise_Detailed_Result.csv")
df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_").str.replace("-", "_")
df = df.dropna(subset=['candidate_name'])
df['gender'] = df['gender'].fillna("Unknown")
df['age'] = df['age'].fillna(df['age'].median())
df['category'] = df['category'].fillna("Unknown")
df['age'] = df['age'].astype(int)

numeric_cols = [
    'total_votes_polled_in_the_constituency', 'valid_votes',
    'votes_secured___general', 'votes_secured___postal',
    'votes_secured___total', 'total_electors',
    '%_of_votes_secured___over_total_electors_in_constituency',
    '%_of_votes_secured___over_total_votes_polled_in_constituency',
    'over_total_valid_votes_polled_in_constituency'
]
df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors='coerce')

# Save NOTA separately for later use
nota_df = df[df['party_name'] == 'NOTA']
df = df[df['party_name'] != 'NOTA']
df.reset_index(drop=True, inplace=True)

# 1. Summary of Votes and Voter Turnout
turnout_df = df.groupby('pc_name').agg({
    'total_electors': 'first',
    'total_votes_polled_in_the_constituency': 'first',
    'valid_votes': 'first'
})
turnout_df['turnout_percentage'] = (turnout_df['total_votes_polled_in_the_constituency'] / turnout_df['total_electors']) * 100

# Summary
summary_stats = turnout_df.describe().round(2)

print("Constituency-wise Turnout Summary:")
print(summary_stats)

print("\nHighest Turnout Constituency:")
print(turnout_df.sort_values(by='turnout_percentage', ascending=False).head(1).round(2))

print("\nLowest Turnout Constituency:")
print(turnout_df.sort_values(by='turnout_percentage').head(1).round(2))




# 2. Party-wise Vote Share Analysis
party_votes = df.groupby('party_name')['votes_secured___total'].sum().sort_values(ascending=False).head(5)
sns.barplot(x=party_votes.values, y=party_votes.index)
plt.title("Top 5 Parties by Vote Share")
plt.xlabel("Total Votes")
plt.ylabel("Party")
plt.tight_layout()
plt.show()

# 3. Candidate Demographics Insights
# Gender Pie Chart
gender_counts = df['gender'].value_counts()
plt.pie(gender_counts, labels=gender_counts.index, autopct='%1.1f%%', startangle=140)
plt.title("Gender Distribution of Candidates")
plt.axis('equal')
plt.show()

# Age Histogram
sns.histplot(df['age'], bins=20, kde=True)
plt.title("Age Distribution of Candidates")
plt.xlabel("Age")
plt.ylabel("Count")
plt.show()

# 4. Constituency-wise Winning Margins
df_sorted = df.sort_values(['pc_name', 'votes_secured___total'], ascending=[True, False])
top2 = df_sorted.groupby('pc_name').head(2)
margins = top2.groupby('pc_name')['votes_secured___total'].apply(lambda x: x.iloc[0] - x.iloc[1])
margins = margins.reset_index(name='margin')

sns.histplot(margins['margin'], bins=30, kde=True)
plt.title("Winning Margin Distribution")
plt.xlabel("Vote Margin")
plt.ylabel("Number of Constituencies")
plt.tight_layout()
plt.show()

# 5. Correlation Between Variables
correlation = df[numeric_cols].corr().round(2)
sns.heatmap(correlation, annot=True, cmap='coolwarm')
plt.title("Correlation Heatmap")
plt.show()

# 6. Category-Wise Representation
sns.countplot(y='category', data=df, order=df['category'].value_counts().index)
plt.title("Category-wise Representation of Candidates")
plt.xlabel("Number of Candidates")
plt.ylabel("Category")
plt.show()

# 7. NOTA Impact Analysis
nota_votes = nota_df[['pc_name', 'votes_secured___total']].rename(columns={'votes_secured___total': 'nota_votes'})
nota_votes = nota_votes.set_index('pc_name')
re = df.groupby('pc_name')['votes_secured___total'].sum().to_frame(name='total_votes')
merged_nota = re.merge(nota_votes, left_index=True, right_index=True, how='left')
merged_nota['nota_votes'] = merged_nota['nota_votes'].fillna(0)
merged_nota = merged_nota.sort_values(by='nota_votes', ascending=False)
sns.barplot(x=merged_nota['nota_votes'].head(20), y=merged_nota.head(20).index)
plt.title("Top 20 Constituencies by NOTA Votes")
plt.xlabel("NOTA Votes")
plt.ylabel("Constituency")
plt.tight_layout()
plt.show()
#8.Total Votes Polled vs Valid Votes for Top 10 Constituencies by Total Electors
top_constituencies = df.groupby('pc_name')['total_electors'].first().sort_values(ascending=False).head(10).index

votes_df = df[df['pc_name'].isin(top_constituencies)].groupby('pc_name').agg({
    'total_votes_polled_in_the_constituency': 'first',
    'valid_votes': 'first'
}).reset_index()

plt.figure(figsize=(10, 6))
sns.lineplot(x='pc_name', y='total_votes_polled_in_the_constituency', data=votes_df, label='Total Votes Polled', marker='o')
sns.lineplot(x='pc_name', y='valid_votes', data=votes_df, label='Valid Votes', marker='s')
plt.xticks(rotation=45)
plt.title("Total Votes Polled vs Valid Votes (Top 10 Constituencies by Electors)")
plt.xlabel("Constituency")
plt.ylabel("Votes")
plt.legend()
plt.tight_layout()
plt.show()

# -*- coding: utf-8 -*-
"""NextLabs coding Q3.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1n3jFHwMtbJbpUsVHEFI90anchmvLfOkk

### Importing Required Libraries
"""

import pandas as pd

"""### Read Data from Multiple Sheets"""

# Function to read all sheets from an Excel file and combine them into a single DataFrame
def load_data_from_excel(file_path):
    all_sheets = pd.read_excel(file_path, sheet_name=None)
    df_list = []
    for sheet_name, df in all_sheets.items():
        df['School'] = sheet_name
        df_list.append(df)
    combined_df = pd.concat(df_list, ignore_index=True)
    return combined_df

# Load data from all Excel files
data_2019 = load_data_from_excel('Bangalore Schools 2019.xlsx')
data_2020 = load_data_from_excel('Bangalore Schools 2020.xlsx')
data_2021 = load_data_from_excel('Bangalore Schools 2021.xlsx')

# Displaying the first few rows of each combined DataFrame
print(data_2019.head())
print(data_2020.head())
print(data_2021.head())

# Merging the data from the three years based on 'Student Roll' and 'Student Name'
merged_data = pd.merge(data_2019, data_2020, on=['Student Roll', 'Student Name', 'School'], suffixes=('_2019', '_2020'))
merged_data = pd.merge(merged_data, data_2021, on=['Student Roll', 'Student Name', 'School'])

merged_data['Total_2019'] = merged_data[[f'{subj}_2019' for subj in subjects]].sum(axis=1)
merged_data['Total_2020'] = merged_data[[f'{subj}_2020' for subj in subjects]].sum(axis=1)
merged_data['Total_2021'] = merged_data[subjects].sum(axis=1)  # 2021 columns are not suffixed

merged_data['Cumulative_Total'] = merged_data[['Total_2019', 'Total_2020', 'Total_2021']].sum(axis=1)

# Display the merged data
print(merged_data.head())

"""*   Here, with the help of read function we can take an Excel file and read all its sheets.
*   And the combined results of first few rows from all the sheets are displayed as output which are nothing but marks of different students in from different schools for the years of 2019, 2020, 2021.

### 1. Reward the top performer (student) of each school based on cumulative marks scored in last three years for all the subjects
"""

# Finding the top performer for each school
top_performers = merged_data.loc[merged_data.groupby('School')['Cumulative_Total'].idxmax()]

# Displaying the top performer details
print(top_performers[['Student Roll', 'Student Name', 'School', 'Cumulative_Total']])

"""* The sum of the marks for each subject across the three years is calculated and  then those marks are cumulated to identify the top performer.
 * Then the students with the highest cumulative marks is displayed as result.

Based on result we can see the toppers from different schools with highest cumulative marks. This can help recognize and reward students who made significant progress.

### 2. Rank each student within their own school based on their total marks scored in the year 2020 and compare the marks of Rank 10 for each school by arranging them in descending order
"""

# Calculating the rank of each student within their school based on their total marks in 2020
merged_data['Rank_2020'] = merged_data.groupby('School')['Total_2020'].rank(method='min', ascending=False)

# Finding the marks of the student ranked 10th in each school
rank_10_marks = merged_data[merged_data['Rank_2020'] == 10].sort_values(by='Total_2020', ascending=False)

# Displaying the details of students ranked 10th in their school
print(rank_10_marks[['Student Roll', 'Student Name', 'School', 'Total_2020']])

"""We rank the students within each school based on their total marks in 2020 and extract the marks of the student who ranked 10th in each school.

This may help students and parents choose schools based on specific academic strengths.

### 3. Find out students with the highest improvement for each subject from 2019-21 combining all the schools together
"""

# Calculating the improvement for each subject from 2019 to 2021
for subject in subjects:
    merged_data[f'Improvement_{subject}'] = merged_data[f'{subject}_2020'] - merged_data[f'{subject}_2019']

# Finding the students with the highest improvement for each subject
highest_improvement_students = {}
for subject in subjects:
    max_improvement = merged_data[f'Improvement_{subject}'].max()
    student = merged_data.loc[merged_data[f'Improvement_{subject}'] == max_improvement, ['Student Roll', 'Student Name', 'School', f'Improvement_{subject}']]
    highest_improvement_students[subject] = student

# Displaying the students with the highest improvement for each subject
highest_improvement_students_df = pd.concat(highest_improvement_students)
highest_improvement_students_df.reset_index(drop=True, inplace=True)
print(highest_improvement_students_df)

"""### 4. Identify best school for Arts, Science and Commerce streams based on marks scored by students in respective subjects for those streams in last three years"""

# Define the subjects for each stream
arts_subjects = ['Hindi', 'English', 'History', 'Geography', 'Civics']
science_subjects = ['Mathematics', 'Physics', 'Chemistry', 'Biology', 'Computer Science']
commerce_subjects = ['Hindi', 'English', 'Mathematics', 'Computer Science', 'Physical Education']

# Calculate the average marks for each stream for each school over the three years
stream_avg = merged_data.groupby('School').apply(
    lambda x: pd.Series({
        'Arts_Avg': x[[f'{subj}_2019' for subj in arts_subjects] + [f'{subj}_2020' for subj in arts_subjects] + arts_subjects].mean().mean(),
        'Science_Avg': x[[f'{subj}_2019' for subj in science_subjects] + [f'{subj}_2020' for subj in science_subjects] + science_subjects].mean().mean(),
        'Commerce_Avg': x[[f'{subj}_2019' for subj in commerce_subjects] + [f'{subj}_2020' for subj in commerce_subjects] + commerce_subjects].mean().mean()
    })
)

# Identify the best school for each stream based on average marks
best_school_arts = stream_avg['Arts_Avg'].idxmax()
best_school_science = stream_avg['Science_Avg'].idxmax()
best_school_commerce = stream_avg['Commerce_Avg'].idxmax()

print(f"Best school for Arts: {best_school_arts}")
print(f"Best school for Science: {best_school_science}")
print(f"Best school for Commerce: {best_school_commerce}")

"""### 5. calculate for each school how many students were in each category based on the avg. marks obtained each year"""

# Define the categories
bins = [0, 20, 40, 60, 80, 100]
labels = ['Very Poor', 'Poor', 'Average', 'Good', 'Very Good']

# Categorize the marks for each subject for each year and count the number of students in each category for each school
category_counts = {}

# Only iterate over years that exist in the data
for year in ['2019', '2020']: # Removed '2021' as it was causing the KeyError
    year_data = merged_data[[f'{subj}_{year}' for subj in subjects] + ['School']]
    year_data.columns = subjects + ['School']
    year_data = year_data.set_index('School')

    categorized_data = year_data.apply(lambda x: pd.cut(x, bins=bins, labels=labels).value_counts()).unstack().reset_index()
    categorized_data.columns = ['School', 'Category', f'Count_{year}']
    category_counts[year] = categorized_data

# Merging the counts for each year
category_counts_df = category_counts['2019']
for year in ['2020']: # Removed '2021' here as well
    category_counts_df = category_counts_df.merge(category_counts[year], on=['School', 'Category'], how='outer')

# Displaying the category counts
print(category_counts_df)

"""* We categorize the marks for each subject into the defined sections (Very Poor, Poor, Average, Good, Very Good).
* We count the number of students in the "Good" and "Very Good" categories for each year.
* The count the number of students in each category is also visible in results.

### 6.  Which is the best school for each year 2019, 2020 and 2021 based on highest no. of students in Good and Very Good category
"""

# Calculating the total number of students in Good and Very Good categories for each school and year
good_categories = ['Good', 'Very Good']
best_schools_per_year = {}
for year in ['2019', '2020']: #Removed Year 2021 as it is causing Key error
    good_students_count = category_counts_df[category_counts_df['Category'].isin(good_categories)][['School', f'Count_{year}']].groupby('School').sum()
    best_school = good_students_count[f'Count_{year}'].idxmax()
    best_schools_per_year[year] = best_school

# Displaying the best school for each year
print(best_schools_per_year)

"""* The best school for each year based on the number of students in the "Good" and "Very Good" categories.
* We identify the school based on the highest count of "Good" and "Very Good" categories for each year.
* This helps recognize schools with consistently high academic performance year over year.

### 7.  Which is the fastest-growing School in Bangalore (Overall and Streamwise)?
"""

# Calculating the growth rate for each school and stream
stream_growth = merged_data.groupby('School').apply(
    lambda x: pd.Series({
        'Arts_Growth': ((x[[f'{subj}_2020' for subj in arts_subjects]].mean().mean() - x[[f'{subj}_2019' for subj in arts_subjects]].mean().mean()) / x[[f'{subj}_2019' for subj in arts_subjects]].mean().mean()) * 100,
        'Science_Growth': ((x[[f'{subj}_2020' for subj in science_subjects]].mean().mean() - x[[f'{subj}_2019' for subj in science_subjects]].mean().mean()) / x[[f'{subj}_2019' for subj in science_subjects]].mean().mean()) * 100,
        'Commerce_Growth': ((x[[f'{subj}_2020' for subj in commerce_subjects]].mean().mean() - x[[f'{subj}_2019' for subj in commerce_subjects]].mean().mean()) / x[[f'{subj}_2019' for subj in commerce_subjects]].mean().mean()) * 100
    })
)

# Identifying the fastest-growing school overall and streamwise
fastest_growing_school_overall = stream_growth.mean(axis=1).idxmax()
fastest_growing_school_arts = stream_growth['Arts_Growth'].idxmax()
fastest_growing_school_science = stream_growth['Science_Growth'].idxmax()
fastest_growing_school_commerce = stream_growth['Commerce_Growth'].idxmax()

print(f"Fastest growing school overall: {fastest_growing_school_overall}")
print(f"Fastest growing school for Arts: {fastest_growing_school_arts}")
print(f"Fastest growing school for Science: {fastest_growing_school_science}")
print(f"Fastest growing school for Commerce: {fastest_growing_school_commerce}")

"""We calculate the total marks for each stream by summing the marks for relevant subjects across the three years and identify the school with the highest average marks for each stream. As per results we can notice that International school is best in all streams frobased on combined data

# **Summary Interpretation:**

**Top Performers:** The top students in each school based on cumulative marks.

**Competitive Environment:** Insights into the academic competitiveness within each school by looking at the marks of the 10th-ranked student.

**Improvement Recognition:** Students who have shown the highest improvement in each subject.

**Stream-wise Best Schools:** Identification of schools that excel in Arts, Science, and Commerce streams.

**Performance Distribution:** Distribution of student performance across different categories within each school.

**Consistent Performance:** Schools that consistently have the highest number of students in the "Good" and "Very Good" categories.

**Growth Recognition:** Schools that have shown the most significant improvement in average marks, indicating effective academic programs.

These insights can be used to guide students in choosing schools, recognizing top performers, and identifying schools with effective academic programs.
"""
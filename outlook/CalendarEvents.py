import win32com.client
import datetime 
import pandas as pd
import numpy as np


class CalendarEvents:

    def __init__(self, start_date: str, end_date: str, date_format: str = "%Y-%m-%d"):

        Outlook = win32com.client.Dispatch("Outlook.Application")
        self.namespace = Outlook.GetNamespace("MAPI")

        self.calendar = self.namespace.GetDefaultFolder(9).Items 

        self.calendar.Sort("[Start]")
        self.calendar.IncludeRecurrences = "True"

        self.start_date = datetime.datetime.strptime(start_date, date_format).strftime("%m/%d/%Y")
        self.end_date = datetime.datetime.strptime(end_date, date_format) + datetime.timedelta(days = 1)
        self.end_date = self.end_date.strftime("%m/%d/%Y")

        date_restriction = f"[Start] >= '{self.start_date}' AND [End] <= '{self.end_date}'"

        self.calendar_events = self.calendar.Restrict(date_restriction)
        self.df = self.create_dataframe()


    def create_dataframe(self):
        df = pd.DataFrame(columns=["Subject", "Date", "Duration", "Category"])

        for index, event in enumerate(self.calendar_events):
            event_row_data = [event.Subject, event.Start.strftime("%m/%d/%Y"), event.Duration, event.Categories]
            df.loc[index] = event_row_data

        df["Category"] = df["Category"].str.replace(r"^$", "None")
        df = df[df["Category"] != 'Ignore']

        return df

    
    def daily_hours_summary(self):
        df = self.df[["Date","Duration"]].groupby(by=["Date"]).sum()
        df["Hours"] = df["Duration"].apply(lambda val: val / 60)
        return df


    def category_summary(self):
        total_minutes = int(self.df[["Duration"]].sum())
        df = self.df[["Category","Duration"]].groupby(by=["Category"]).sum()
        df["Percentage"] = df["Duration"].apply(lambda val: val / total_minutes)
        df = df.style.format({"Percentage": '{:,.2%}'.format})
        return df


    def daily_category_summary(self):
        daily_duration = self.df[["Date","Duration"]].groupby(by=["Date"]).sum()
        daily_duration.columns = ["DailyDuration"]

        df = self.df[["Date","Category","Duration"]]
        df = daily_duration.merge(df, on="Date",how="inner")

        df = df.groupby(by=["Date","Category","DailyDuration"]).sum()

        def cal_percentage(row):
            return row["Duration"] / row["DailyDuration"]
            
        df.reset_index(inplace=True)
        df["Percentage"] = df.apply(lambda row: cal_percentage(row), axis = 1)

        df = df.pivot(index='Date', columns='Category', values='Percentage')
        df.fillna(value=0, inplace=True)

        for col in df:
            df[col] = df[col].apply(lambda val: '{:,.2%}'.format(val))

        # df = self.daily_hours_summary().merge(df, on="Date",how="inner")

        return df

    def daily_summary(self):
        return self.daily_hours_summary().merge(self.daily_category_summary(), on="Date",how="inner")


class TodayCalendarEvents(CalendarEvents):
     def __init__(self):
        self.today = datetime.date.today().strftime("%Y-%m-%d")
        super().__init__(self.today, self.today)
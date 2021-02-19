import csv
import os
import os.path, time
import fnmatch
from datetime import date
from datetime import datetime
import pandas as pd


def skip_if_not_expected_file_type(path, file_type=".csv"):
    if not file_type in path:
        return True
    else:
        return False


def look_for_errors_in(row):
    error_code = "SqlException"
    if error_code in row.ErrorCode:
        return row.ErrorMessage


def review_file(file, file_path, df):
    try:
        file_df = pd.read_csv(file_path, header=None)
        file_df = file_df[file_df.columns[-2:]].copy()
        file_df.columns = ["ErrorMessage", "ErrorCode"]

        file_df = file_df[file_df["ErrorCode"] == "SqlException"]

        file_df.drop_duplicates(inplace=True)
        file_df.dropna(how="all", inplace=True)
        df = df.append(file_df)
        df["ErrorMessage"] = df["ErrorMessage"].str.replace("\d+", "")
        df.drop_duplicates(inplace=True)

        return df

    except Exception as ex:
        print(f"{type(ex)} Error with file: {file}")


def loop_thru_folder(
    folder_location,
    earliest_file_date,
    latest_file_date=str(datetime.today()),
    maximum_len=100,
):
    # ignore_file = 0
    # skip_analyst_fix = False
    # skip_analyst_change = False
    # skip_campaign_fix = False

    df = pd.DataFrame(columns=["ErrorMessage", "ErrorCode"])

    for path, subdir, files in os.walk(folder_location):
        print(f"Reviewing Folder... {subdir}")

        for file in files:
            if len(df) > maximum_len:
                return df
            file_path = os.path.join(path, file)

            if skip_if_not_expected_file_type(file_path, ".csv"):
                continue

            file_creation_date = ""
            file_size = 0
            try:
                file_creation_date = str(
                    datetime.fromtimestamp(os.path.getctime(file_path))
                )[:10]
                file_size = os.path.getsize(file_path)
            except:
                print(
                    f"Error getting properties of ({os.path.basename(file_path)[:50]}) Review Manually."
                )

            if file_creation_date < earliest_file_date:
                continue
            if file_creation_date > latest_file_date:
                continue
            if file_size == 0:
                continue

            print(f"Reading {file}, Size {file_size}")
            df = review_file(file, file_path, df)
            print(f"LEN of error df {len(df)}")

    return df


def export_file(df, name, index=False):
    output_path = os.path.dirname(__file__) + "\\output"
    file_name = f"{output_path}\\ErrorCollection_{name}_{datetime.today().strftime('%Y-%m-%d %H%M%S')}.xlsx"
    excel_file = pd.ExcelWriter(file_name)
    df.to_excel(excel_file, index=index)
    excel_file.save()


def framework():
    folder_location = (
        "\\\\prodjobdata.extendhealth.com\\EligibilityFileImportNotImported\\2021\\2"
    )
    # folder_location = r'\\\\secureshare\\Encrypted Share\\Delivery Management\\Eligibility\\ErrorOutputs\\EtlErrors'
    earliest_file_date = "2021-02-01"
    latest_file_date = str(datetime.today())

    df = loop_thru_folder(folder_location, earliest_file_date, latest_file_date)
    export_file(df, "SqlException")


if __name__ == "__main__":
    framework()
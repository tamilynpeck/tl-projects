import csv
import os
import os.path, time
import fnmatch
from datetime import date
from datetime import datetime
import pandas as pd

ERROR_CODE = "SqlException"


def skip_if_not_expected_file_type(path, file_type=".csv"):
    if not file_type in path:
        return True
    else:
        return False


def review_file(file_name, file_path, df):
    try:
        file_df = pd.read_csv(file_path, header=None)
        columns = [file_df.columns[1]]
        columns.extend(file_df.columns[-2:])
        file_df = file_df[columns].copy()
        file_df.columns = ["FileName", "ErrorMessage", "ErrorCode"]
        file_df = file_df[file_df["ErrorCode"].str.contains(ERROR_CODE)]
        # file_df = file_df[file_df["ErrorCode"] == ERROR_CODE]

        file_df.drop_duplicates(inplace=True)
        file_df.dropna(how="all", inplace=True)
        df = df.append(file_df)
        df["ErrorMessage"] = df["ErrorMessage"].str.replace(r"\d+", "", regex=True)
        df.drop_duplicates(inplace=True)

        return df

    except Exception as ex:
        print(f"{type(ex)} Error with file: {file_name}")


def loop_thru_folder(
    folder_location,
    earliest_file_date,
    latest_file_date=str(datetime.today()),
    maximum_len=100,
    limit_client_code=None,
    # skip_analyst_fix = False
    # skip_analyst_change = False
    # skip_campaign_fix = False
):

    df = pd.DataFrame(columns=["FileName", "ErrorMessage", "ErrorCode"])

    for path, subdir, files in os.walk(folder_location):
        print(f"Reviewing Folder... {subdir}")

        for file_name in files:
            if len(df) > maximum_len:
                return df
            file_path = os.path.join(path, file_name)

            if limit_client_code not in file_name:
                continue

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

            print(f"Reading {file_name}, Size {file_size}")
            df = review_file(file_name, file_path, df)
            print(f"Number Of Errors Found: {len(df)}")

    return df


def export_file(df, name, index=False):
    output_path = os.path.dirname(__file__) + "\\output"
    file_name = f"{output_path}\\ErrorCollection_{name}_{datetime.today().strftime('%Y-%m-%d %H%M%S')}.xlsx"
    excel_file = pd.ExcelWriter(file_name)
    df.to_excel(excel_file, index=index)
    excel_file.save()


def framework():
    folder_location = (
        "\\\\prodjobdata.extendhealth.com\\EligibilityFileImportNotImported\\2021"
    )
    earliest_file_date = "2020-01-01"
    latest_file_date = str(datetime.today())
    limit_client_code = "AMTR"

    df = loop_thru_folder(
        folder_location=folder_location,
        earliest_file_date=earliest_file_date,
        latest_file_date=latest_file_date,
        limit_client_code=limit_client_code,
    )
    export_file(df, f"SqlException_{limit_client_code}")


if __name__ == "__main__":
    framework()
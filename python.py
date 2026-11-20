import numpy as np
import pandas as pd

COLUMNS = ['Name', 'Marks', 'Income', 'Attendance']
NUMERIC = ['Marks', 'Income', 'Attendance']


def load_students(csv_path):
    """Load the CSV with Pandas, skip invalid/missing rows and print a message for each."""

    def bad_line(fields):
        name = fields[0].strip() if fields and fields[0].strip() else "unknown"
        print(f"Invalid row for {name}: expected 4 values. Row skipped.")
        return None  # skip this line

    try:
        raw = pd.read_csv(csv_path, header=None, names=COLUMNS, dtype=str,
                          keep_default_na=False, skipinitialspace=True,
                          engine='python', on_bad_lines=bad_line)
    except FileNotFoundError:
        print(f"File {csv_path} not found.")
        return pd.DataFrame(columns=COLUMNS)
    except pd.errors.EmptyDataError:
        return pd.DataFrame(columns=COLUMNS)

    raw = raw.fillna('')
    if not raw.empty:
        first_row = raw.iloc[0].astype(str).str.strip().str.lower().tolist()

        if first_row == [col.lower() for col in COLUMNS]:
            raw = raw.iloc[1:].reset_index(drop=True)
    valid_rows = []

    for _, row in raw.iterrows():
        name = row['Name'].strip()
        if not name:
            print("Missing name. Row skipped.")
            continue

        record = {'Name': name}
        ok = True
        for field in NUMERIC:
            value = row[field].strip()
            if value == '':
                print(f"Missing {field.lower()} for {name}. Row skipped.")
                ok = False
                break
            try:
                number = float(value)
                if not np.isfinite(number):
                    raise ValueError
                if field == 'Marks' and not 0 <= number <= 100:
                    print(f"Invalid marks for {name}: '{value}'. Row skipped.")
                    ok = False
                    break

                if field == 'Attendance' and not 0 <= number <= 100:
                    print(f"Invalid attendance for {name}: '{value}'. Row skipped.")
                    ok = False
                    break

                if field == 'Income' and number < 0:
                    print(f"Invalid income for {name}: '{value}'. Row skipped.")
                    ok = False
                    break
                record[field] = number
            except ValueError:
                print(f"Invalid {field.lower()} for {name}: '{value}'. Row skipped.")
                ok = False
                break
        if ok:
            valid_rows.append(record)

    return pd.DataFrame(valid_rows, columns=COLUMNS)


def apply_rules(df):
    """Add Result and Scholarship columns using np.where / np.select conditions."""
    eligible = (df['Attendance'] >= 75) & (df['Marks'] >= 75) & (df['Income'] <= 500000)
    full = eligible & (df['Marks'] >= 90) & (df['Income'] <= 300000)

    df['Result'] = np.where(~eligible, 'Not Eligible', np.where(full, 'Full', 'Partial'))
    df['Scholarship'] = np.select(
        [df['Result'] == 'Full', df['Result'] == 'Partial'],
        [50000, 25000],
        default=0
    )
    return df


def show_eligibility(df):
    for _, row in df.iterrows():
        if row['Result'] == 'Not Eligible':
            print(f"{row['Name']} | Not Eligible")
        else:
            print(f"{row['Name']} | {row['Result']} | Rs. {int(row['Scholarship'])}")


def show_summary(df):
    eligible_df = df[df['Result'] != 'Not Eligible']
    eligible_count = len(eligible_df)
    not_eligible_count = len(df) - eligible_count
    full_count = int((df['Result'] == 'Full').sum())
    partial_count = int((df['Result'] == 'Partial').sum())
    total_amount = int(df['Scholarship'].sum())
    avg_marks = eligible_df['Marks'].mean() if eligible_count > 0 else 0.0

    print(f"Eligible: {eligible_count} | Not Eligible: {not_eligible_count} "
          f"| Full: {full_count} | Partial: {partial_count}")
    print(f"Total scholarship: Rs. {total_amount} | Average marks (eligible): {avg_marks:.2f}")


def filter_by_marks(df, min_marks):
    filtered = df[df['Marks'] >= min_marks]

    if filtered.empty:
        print("No students found.")
        return

    for _, row in filtered.iterrows():
        print(f"{row['Name']} | {row['Marks']:g}")


def main():
    df = load_students("students.csv")
    if df.empty:
        return
    df = apply_rules(df)

    while True:
        print("\n1. Eligibility\n2. Summary\n3. Filter by minimum marks\n4. Exit")
        try:
            choice = input("Enter choice: ").strip()
        except EOFError:
            print("\nNo more input. Exiting.")
            break

        if choice == '1':
            show_eligibility(df)
        elif choice == '2':
            show_summary(df)
        elif choice == '3':
            try:
                min_marks = float(input("Enter minimum marks: ").strip())
            except ValueError:
                print("Invalid marks value.")
                continue
            filter_by_marks(df, min_marks)
        elif choice == '4':
            break
        else:
            print("Invalid choice. Please enter 1-4.")


if __name__ == '__main__':
    main()

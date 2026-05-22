from datetime import date, timedelta
import pandas as pd


def get_prev_month_range():
    today = date.today()
    first_day_current_month = today.replace(day=1)
    end_prev_month = first_day_current_month - timedelta(days=1)
    start_prev_month = end_prev_month.replace(day=1)
    return start_prev_month, end_prev_month


class MonthlyReport:
    def __init__(self):
        self.start_prev_month, self.end_prev_month = get_prev_month_range()
        self.prev_month = self.start_prev_month.month
        self.prev_year = self.start_prev_month.year

    async def _drop_tz(self, df: pd.DataFrame) -> pd.DataFrame:
        for col in df.columns:
            if pd.api.types.is_datetime64_any_dtype(df[col]):
                try:
                    df[col] = df[col].dt.tz_convert(None)
                except Exception:
                    try:
                        df[col] = df[col].dt.tz_localize(None)
                    except Exception:
                        pass
            elif df[col].dtype == "object":
                def normalize_value(x):
                    if isinstance(x, pd.Timestamp):
                        if x.tz is not None:
                            return x.tz_localize(None)
                        return x
                    return x

                df[col] = df[col].apply(normalize_value)

        return df
from math import exp
import polars as pl
pl.Config.set_tbl_cols(1000)


class Tools():
    def __init__(self, df: pl.DataFrame):
        self.df = df
    
    def explore(self) -> pl.DataFrame:
        """
        Explore the dataframe and return a summary of the data.
        Equivalent to pandas `describe(include='all')`.
        """
        return self.df.describe()

    def columns(self) -> list[str]:
        """
        Return the columns of the dataframe.
        """
        return self.df.columns

    def shape(self) -> tuple[int, int]:
        """
        Return the shape of the dataframe as (rows, columns).
        """
        return self.df.shape

    def head(self, n: int = 5) -> pl.DataFrame:
        """
        Return the first n rows of the dataframe.
        """
        return self.df.head(n)

    def tail(self, n: int = 5) -> pl.DataFrame:
        """
        Return the last n rows of the dataframe.
        """
        return self.df.tail(n)

    def info(self) -> str:
        """Return schema and basic information of the dataframe"""
        info_lines = [f"Shape: {self.df.shape}", "Schema:"]
        for name, dtype in self.df.schema.items():
            info_lines.append(f"  {name}: {dtype}")
        return "\n".join(info_lines)

    def sql(self, query: str):
        """
        execute a sql query using polars
        """
        try:
            return self.df.sql(query)
        except Exception as e:
            error_msg = f"SQL Error: {str(e)}"
            print(error_msg)
            return {"error": error_msg, "status": "failed"}


if __name__ == "__main__":
    df = pl.read_csv("../data/data.csv")
    print(Tools(df).explore())
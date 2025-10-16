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

    def sql(self, query: str) -> pl.DataFrame:
        """
        execute a sql query using polars
        """
        try:
            return self.df.sql(query)
        except Exception as e:
            print(f"SQL query error: {str(e)}")
            print("Please check your query syntax and try again.")
            # Return empty DataFrame with same schema as original
            return pl.DataFrame(schema=self.df.schema)


if __name__ == "__main__":
    df = pl.read_csv("../data/data.csv")
    print(Tools(df).explore())
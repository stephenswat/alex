import enum


class Pattern(str, enum.Enum):
    MMijk = "MMijk"
    MMikj = "MMikj"
    MMTijk = "MMTijk"
    MMTikj = "MMTikj"
    Jacobi2D = "Jacobi2D"
    Himeno = "Himeno"
    Cholesky = "Cholesky"
    Crout = "Crout"

    def __str__(self):
        return self.value


class Precision(str, enum.Enum):
    Single = "single"
    Double = "double"

    def __str__(self):
        return self.value

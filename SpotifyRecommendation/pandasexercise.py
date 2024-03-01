import pandas as pd

# DATAFRAME
mydataset = {
  'cars': ["Porsche", "Ferrari", "Ford"],
  'passings': [3, 7, 2]
}

myvar = pd.DataFrame(mydataset)

print(myvar)


data = {
  "calories": [420, 380, 390],
  "duration": [50, 40, 45]
}

myvar = pd.DataFrame(data)

print(myvar)

o = pd.DataFrame({'Bob': ['I liked it.', 'It was awful.'],
              'Sue': ['Pretty good.', 'Bland.']},
             index=['Product A', 'Product B'])
print(o)




# SERIES
series_set = ["taylor", "maclaurin"]
series = pd.Series(series_set)
print(series[0])
# CREATE LABEL
series = pd.Series(series_set, index=["a", "b"])
print(series)
print(series["a"])






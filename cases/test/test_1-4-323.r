
library(tidyverse)

f <- function(cars){
    x <- cars %>% mutate(rowname = row_number()) %>% pivot_longer(-rowname, names_to = "column", values_to = "value") %>% group_by(column) %>% mutate(category = case_when((value == min(value)) == TRUE ~ "min", (value == max(value)) == TRUE ~ "max")) %>% drop_na(category) %>% group_by(column, value, category) %>% summarise(rowname = toString(rowname), freq.times = n()) %>% select(2:3, 1, 4, 5)
    return (x)
}

cars = df <- data.frame(
         speed = c(1, 2, 3, 4, 5, 1, 3, 6, 4, 2),
         dist = c(6, 7, 8, 9, 10, 100, 10, 6, 5, 7))

df1 = f(cars)
df2 = myMaxMin(cars)

df1 = unname(df1)
df2 = unname(df2)

assert(all.equal(df1, df2, check.attributes = FALSE))

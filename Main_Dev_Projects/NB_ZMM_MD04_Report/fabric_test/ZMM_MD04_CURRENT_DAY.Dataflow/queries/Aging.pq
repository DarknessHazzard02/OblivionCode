// Made by: Hazzard
// Maps reschedule days to an ordered bucket label (a. Less than 03 days ... i. More than 1 year)
shared Aging = let
    RescheduleBucket = (Days) =>
        if Days >= 365 then "i. More than 1 year"
        else if Days >= 270 then "h. More than 09 months"
        else if Days >= 180 then "g. More than 06 months"
        else if Days >= 90 then "f. More than 03 months"
        else if Days >= 30 then "e. More than 01 month"
        else if Days >= 14 then "d. More than 02 weeks"
        else if Days >= 7 then "c. More than 01 weeks"
        else if Days >= 3 then "b. More than 03 days"
        else "a. Less than 03 days"
in
    RescheduleBucket;

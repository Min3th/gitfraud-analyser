                   GitFraud

These are the rules used to decide whether a commit is fake or not

1.  Commit scripts :

    - Commits on the same hour , same minute everyday
    - Similar commit message , file change length and repo

2.  Extremely minor commits to fill git graph

    - Extremely small file change length
    - Small commit messages

3.  Similar keywords in file change
    - Print statements etc.

# Note CI

Fluxul prin care funcționează Live Review-ul de pe GitHub:

1. Modificarea se face pe **o ramură**, nu direct în `main`
2. Se face **push** pe ramură
3. Se deschide un **Pull Request** spre `main`
4. GitHub pornește automat:
   - acțiunile din `.github/workflows/verify.yml`
   - agentul de code review, care examinează **diff-ul din PR**

**Fără pull request, reviewerul nu are ce vedea.** Aici a fost eroarea:
am împins 10 commit-uri direct în `main`, într-o singură ramură.

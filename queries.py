
# twitter graph matif queries
triangle = '''
R = scan(chushumo:multiway_join:twitter_1m);
-- query(x,y,z,p):-R(x,y),S(y,z),T(z,x)
query = [from R, R as S, R as T
       where R.$1 = S.$0 and
             S.$1 = T.$0 and
             T.$1 = R.$0
       emit R.$0 as x, S.$0 as y, S.$1 as z];
'''

rectangle = '''
R = scan(chushumo:multiway_join:twitter_1m);
query = [from R, R as S, R as T, R as P
       where R.$1 = S.$0 and
             S.$1 = T.$0 and
             T.$1 = P.$0 and
             P.$1 = R.$0
       emit R.$0 as x, S.$0 as y, S.$1 as z, T.$1 as p];
'''

cocktail = '''
R = scan(chushumo:multiway_join:twitter_1m);
-- query(x,y,z,p):-R(x,y),S(y,z),T(z,x),P(x,p)
query = [from
            R, R as S, R as T, R as P
            where R.$1 = S.$0 and
               S.$1 = T.$0 and
               T.$1 = S.$0 and
               P.$0 = S.$0 and
               R.$0 < R.$1 and
               S.$0 < S.$1
         emit R.$0 as x, S.$0 as y, S.$1 as z, P.$1 as p];
'''

two_rings = '''
R = scan(chushumo:multiway_join:twitter_1m);
-- query(x,y,z,p):-R(x,y),S(y,z),T(z,p),P(p,x),K(x,z)
query = [from R, R as S, R as T, R as P, R as K
         where R.$1 = S.$0 and
             S.$1 = T.$0 and
             T.$1 = P.$0 and
             P.$1 = R.$0 and
             K.$0 = R.$0 and
             K.$1 = T.$0 and
             R.$0 < R.$1 and
             S.$0 < S.$1 and
             T.$0 < T.$1 and
             P.$0 > P.$1
        emit R.$0 as x, S.$0 as y, S.$1 as z, T.$1 as p];
'''

clique = '''
R = scan(chushumo:multiway_join:twitter_1m);
-- query(x,y,z,p):-R(x,y),S(y,z),T(z,p),P(p,x),K(x,z),L(y,p)
query = [from R, R as S, R as T, R as P, R as K, R as L
         where R.$1 = S.$0 and
             S.$1 = T.$0 and
             T.$1 = P.$0 and
             P.$1 = R.$0 and
             K.$0 = R.$0 and
             K.$1 = T.$0 and
             L.$0 = S.$1 and
             L.$1 = P.$0 and
             R.$0 < R.$1 and
             S.$0 < S.$1 and
             T.$0 < T.$1 and
             P.$0 > P.$1
         emit R.$0 as x, S.$0 as y, S.$1 as z, T.$1 as p];
'''

# freebase queries
fb_q1 = '''
r1 = scan(actor_a_id); -- 26
r2 = scan(actor_film); -- 1100844
r3 = scan(perform_film); -- 1094294
r4 = scan(actor_b_id); -- 2
r5 = scan(actor_film); -- 1100844
r6 = scan(perform_film); -- 1094294
r7 = scan(perform_film); -- 1094294
r8 = scan(actor_film); -- 1100844
-- Join
query = [from r1,r2,r3,r6,r5,r4,r7,r8
      where
        r1.a_id = r2.actor and
        r2.film = r3.perf_id and
        r3.film_id = r6.film_id and
        r6.film_id = r7.film_id and
        r4.b_id = r5.actor and
        r5.film = r6.perf_id and
        r7.perf_id = r8.film
      emit r8.actor as cast_actor_id];
-- Store
'''

fb_q2 = '''
r1 = scan(couple); -- 87
r2 = scan(actor_film); -- 1,100,844
r3 = scan(perform_film); -- 1,094,294
r4 = scan(actor_film); -- 1,100,844
r5 = scan(perform_film); -- 1,094,294
query = [from r1, r2, r3, r4, r5
      where r1.couple1 = r2.actor and
            r1.couple2 = r4.actor and
            r2.film = r3.perf_id and
            r3.film_id = r5.film_id and
            r4.film = r5.perf_id
      emit r1.couple1 as a, r1.couple2 as b];
'''

fb_q3 = '''
r1 = scan(oscar); -- 202
r2 = scan(honor_award); -- 93,468
r3 = scan(honor_actor); -- 126,238
r4 = scan(honor_year); -- 92,946
-- Query
query = [from r1, r2, r3, r4
      where r1.oscar = r2.award and
            r2.honor = r3.honor and
            r3.honor = r4.honor and
            r4.year >= 1990 and
            r4.year < 2000
      emit r3.actor];
-- Store
'''

fb_q4 = '''
r1 = scan(actor_film); -- 1,100,844
r2 = scan(actor_film); -- 1,100,844
r3 = scan(perform_film); -- 1,094,294
r4 = scan(perform_film); -- 1,094,294
r5 = scan(director_film); -- 190,820
r6 = scan(director_film); -- 190,820
-- query(x) :- r1(x,p1),r2(x,p2),r3(p1,f1),r4(p2,f2),r5(d,f1),r6(d,f2)
query = [from  r6, r4, r2, r1, r3, r5
         where r1.$0 = r2.$0 and
               r1.$1 = r3.$0 and
               r2.$1 = r4.$0 and
               r3.$1 = r5.$1 and
               r4.$1 = r6.$1 and
               r5.$0 = r6.$0
         emit r1.$0 as x, r5.$0 as y];
-- Store
'''

fb_q5 = '''
-- find actor/actor pair which have cooperated in at least two different movies
af = scan(actor_film); -- 1,100,844
pf = scan(perform_film); -- 1,094,294
query = [from
            af as r1, pf as r2,
            af as r3, pf as r4,
            pf as r6, af as r5,
            af as r7, pf as r8
         where r1.$0 = r3.$0 and -- actor 1
               r1.$1 = r2.$0 and -- perf-film
               r2.$1 = r6.$1 and -- the first same film by actor 1 and 2
               r3.$1 = r4.$0 and -- second film by actor 1
               r4.$1 = r8.$1 and -- the second same film by actor 1 and 2
               r5.$0 = r7.$0 and -- actor 2
               r5.$1 = r6.$0 and -- perf-film
               r7.$1 = r8.$0 and
               r2.$1 > r8.$1
         emit r1.$0 as x, r5.$0 as y];
-- Store
'''

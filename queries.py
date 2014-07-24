
# twitter graph matif queries
triangle = '''
R = scan(chushumo:multiway_join:twitter_1m);
-- query(x,y,z,p):-R(x,y),S(y,z),T(z,x)
query = [from R, R as S, R as T
       where R.$1 = S.$0 and
             S.$1 = T.$0 and
             T.$1 = R.$0
       emit R.$0 as x, S.$0 as y, S.$1 as z];
store(query, triangle);
'''

rectangle = '''
R = scan(chushumo:multiway_join:twitter_1m);
rec = [from R, R as S, R as T, R as P
       where R.$1 = S.$0 and
             S.$1 = T.$0 and
             T.$1 = P.$0 and
             P.$1 = R.$0
       emit R.$0 as x, S.$0 as y, S.$1 as z, T.$1 as p];
store(rec, rectangle);
'''

cocktail = '''
R = scan(chushumo:multiway_join:twitter_1m);
-- query(x,y,z,p):-R(x,y),S(y,z),T(z,x),P(x,p)
query = [from
            R, R as S, R as T, R as P
         where R.$1 = S.$0 and
               S.$1 = T.$0 and
               T.$1 = S.$0 and
               P.$0 = S.$0
         emit R.$0 as x, S.$0 as y, S.$1 as z, P.$1 as p];
store(query, cocktail);
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
             K.$1 = T.$0
        emit R.$0 as x, S.$0 as y, S.$1 as z, T.$1 as p];
store(query, two_rings);
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
             L.$1 = P.$0
        emit R.$0 as x, S.$0 as y, S.$1 as z, T.$1 as p];
store(query, clique);
'''

# freebase queries
fb_q1 = '''
r1 = scan(actor_a_id);
r2 = scan(actor_film);
r3 = scan(perform_film);
r4 = scan(actor_b_id);
r5 = scan(actor_film);
r6 = scan(perform_film);
r7 = scan(perform_film);
r8 = scan(actor_film);
-- Join
q1 = [from r6,r3,r2,r1,r5,r4,r7,r8
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
store(q1, fb_q1);
'''

fb_q2 = '''
r1 = scan(couple);
r2 = scan(actor_film);
r3 = scan(perform_film);
r4 = scan(actor_film);
r5 = scan(perform_film);
q2 = [from r1, r2, r3, r4, r5
      where r1.couple1 = r2.actor and
            r1.couple2 = r4.actor and
            r2.film = r3.perf_id and
            r3.film_id = r5.film_id and
            r4.film = r5.perf_id
      emit r1.couple1 as a, r1.couple2 as b];
store(q2, fb_q2);
'''

fb_q3 = '''
r1 = scan(oscar);
r2 = scan(honor_award);
r3 = scan(honor_actor);
r4 = scan(honor_year);
-- Query
q3 = [from r1, r2, r3, r4
      where r1.oscar = r2.award and
            r2.honor = r3.honor and
            r3.honor = r4.honor and
            r4.year >= 1990 and
            r4.year < 2000
      emit r3.actor];
-- Store
store(q3, fb_q3);
'''

fb_q4 = '''

'''

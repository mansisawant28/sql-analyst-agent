# Draft eval questions (Chinook)

Run each query in DB Browser (Execute SQL tab), then paste the result into the Answer line.

## Q1 (easy, one table)
**Question:** How many tracks are in the database?
**SQL:**
```sql
SELECT COUNT(*) AS total_tracks
FROM Track;
```
**Answer:** 
3503

## Q2 (easy, one table)
**Question:** Which country has the most customers?
**SQL:**
```sql
SELECT Country, COUNT(*) AS n
FROM Customer
GROUP BY Country
ORDER BY n DESC
LIMIT 1;
```
**Answer:** 
13

## Q3 (join: Artist + Album)
**Question:** Which artist has the most albums?
**SQL:**
```sql
SELECT ar.Name, COUNT(*) AS album_count
FROM Artist ar
JOIN Album al ON al.ArtistId = ar.ArtistId
GROUP BY ar.ArtistId
ORDER BY album_count DESC
LIMIT 1;
```
**Answer:** 
Iron Maiden 21

## Q4 (join: Customer + Invoice)
**Question:** What are the top 3 countries by total revenue?
**SQL:**
```sql
SELECT c.Country, ROUND(SUM(i.Total), 2) AS revenue
FROM Customer c
JOIN Invoice i ON i.CustomerId = c.CustomerId
GROUP BY c.Country
ORDER BY revenue DESC
LIMIT 3;
```
**Answer:** 
USA 523.06
Canada 303.96
France 195.1

## Q5 (join: Genre + Track)
**Question:** Which genre has the most tracks?
**SQL:**
```sql
SELECT g.Name, COUNT(*) AS track_count
FROM Genre g
JOIN Track t ON t.GenreId = g.GenreId
GROUP BY g.GenreId
ORDER BY track_count DESC
LIMIT 1;
```
**Answer:** 
Rock 1297
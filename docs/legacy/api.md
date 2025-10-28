# LOL API Gateway (generated)

Intelligent proxy for Riot Games API with caching, rate limiting, and match tracking

**Auto-generated from the running service's `/openapi.json`.**

## Endpoints

| Tag | Method | Path | Summary | Path params | Query params | Request | Response | Example |
|---|---|---|---|---|---|---|---|---|
| health | GET | `/health` | Health Check |  |  |  |  |  |
| challenges | GET | `/lol/challenges/v1/challenges/config` | Get All Challenges Config |  | region:string |  |  |  |
| challenges | GET | `/lol/challenges/v1/challenges/{challengeId}/config` | Get Challenge Config | challengeId:integer | region:string |  |  |  |
| challenges | GET | `/lol/challenges/v1/challenges/{challengeId}/leaderboards/by-level/{level}` | Get Challenge Leaderboard | challengeId:integer, level:string | region:string, limit:integer |  |  |  |
| challenges | GET | `/lol/challenges/v1/challenges/{challengeId}/percentiles` | Get Challenge Percentiles | challengeId:integer | region:string |  |  |  |
| challenges | GET | `/lol/challenges/v1/player-data/{puuid}` | Get Player Challenges | puuid:string | region:string |  |  |  |
| champion-mastery | GET | `/lol/champion-mastery/v4/champion-masteries/by-puuid/{puuid}` | Get All Champion Masteries | puuid:string | region:string |  |  |  |
| champion-mastery | GET | `/lol/champion-mastery/v4/champion-masteries/by-puuid/{puuid}/by-champion/{championId}` | Get Champion Mastery | puuid:string, championId:integer | region:string |  |  |  |
| champion-mastery | GET | `/lol/champion-mastery/v4/champion-masteries/by-puuid/{puuid}/top` | Get Top Champion Masteries | puuid:string | region:string, count:integer |  |  |  |
| champion-mastery | GET | `/lol/champion-mastery/v4/scores/by-puuid/{puuid}` | Get Mastery Score | puuid:string | region:string |  |  |  |
| clash | GET | `/lol/clash/v1/players/by-puuid/{puuid}` | Get Clash Player | puuid:string | region:string |  |  |  |
| clash | GET | `/lol/clash/v1/teams/{teamId}` | Get Clash Team | teamId:string | region:string |  |  |  |
| clash | GET | `/lol/clash/v1/tournaments` | Get Clash Tournaments |  | region:string |  |  |  |
| clash | GET | `/lol/clash/v1/tournaments/by-team/{teamId}` | Get Clash Tournament By Team | teamId:string | region:string |  |  |  |
| clash | GET | `/lol/clash/v1/tournaments/{tournamentId}` | Get Clash Tournament | tournamentId:integer | region:string |  |  |  |
| league | GET | `/lol/league/v4/challengerleagues/by-queue/{queue}` | Get Challenger League | queue:string | region:string |  |  |  |
| league | GET | `/lol/league/v4/entries/by-summoner/{encryptedSummonerId}` | Get League Entries By Summoner | encryptedSummonerId:string | region:string |  |  |  |
| league | GET | `/lol/league/v4/grandmasterleagues/by-queue/{queue}` | Get Grandmaster League | queue:string | region:string |  |  |  |
| league | GET | `/lol/league/v4/masterleagues/by-queue/{queue}` | Get Master League | queue:string | region:string |  |  |  |
| match | GET | `/lol/match/v5/matches/by-puuid/{puuid}/ids` | Get Match Ids By Puuid | puuid:string | region:string, start:integer, count:integer |  |  |  |
| match | GET | `/lol/match/v5/matches/{matchId}` | Get Match | matchId:string | region:string, force:boolean |  |  |  |
| match | GET | `/lol/match/v5/matches/{matchId}/timeline` | Get Match Timeline | matchId:string | region:string |  |  |  |
| champion | GET | `/lol/platform/v3/champion-rotations` | Get Champion Rotations |  | region:string |  |  |  |
| spectator | GET | `/lol/spectator/v5/active-games/by-summoner/{puuid}` | Get Active Game | puuid:string | region:string |  |  |  |
| spectator | GET | `/lol/spectator/v5/featured-games` | Get Featured Games |  | region:string |  |  |  |
| platform | GET | `/lol/status/v4/platform-data` | Get Platform Status |  | region:string |  |  |  |
| summoner | GET | `/lol/summoner/v4/summoners/by-name/{summonerName}` | Get Summoner By Name | summonerName:string | region:string |  |  |  |
| summoner | GET | `/lol/summoner/v4/summoners/by-puuid/{encryptedPUUID}` | Get Summoner By Puuid | encryptedPUUID:string | region:string |  |  |  |
| summoner | GET | `/lol/summoner/v4/summoners/{encryptedSummonerId}` | Get Summoner By Id | encryptedSummonerId:string | region:string |  |  |  |
| account | GET | `/riot/account/v1/accounts/by-puuid/{puuid}` | Get Account By Puuid | puuid:string | region:string |  |  |  |
| account | GET | `/riot/account/v1/accounts/by-riot-id/{gameName}/{tagLine}` | Get Account By Riot Id | gameName:string, tagLine:string | region:string |  |  |  |
| account | GET | `/riot/account/v1/active-shards/by-game/{game}/by-puuid/{puuid}` | Get Active Shard | game:string, puuid:string | region:string |  |  |  |

For interactive docs visit <http://127.0.0.1:8080/docs> when the gateway is running.
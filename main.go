package main

import (
	"bytes"
	"database/sql"
	"encoding/json"
	"fmt"
	"github.com/bwmarrin/discordgo"
	_ "github.com/go-sql-driver/mysql"
	"github.com/spf13/viper"
	"log"
	"net/http"
	"os"
	"os/signal"
	"regexp"
	"strconv"
	"strings"
	"syscall"
	"time"
)

func init() {
	viper.SetConfigName("config")
	viper.AddConfigPath(".")
	viper.SetConfigType("json")

	cfgerr := viper.ReadInConfig()
	if cfgerr != nil {
		panic(fmt.Errorf("Fatal error config file: %s \n", cfgerr))
	}
}

const (
	EXIT_COMMAND = "exit"
)

// Make discord session globally available
var dg *discordgo.Session

func main() {
	var err error
	dg, err = discordgo.New("Bot " + viper.GetString("DiscordBotToken"))
	if err != nil {
		fmt.Println("error creating Discord session,", err)
		return
	}

	// Open a websocket connection to Discord and begin listening.
	err = dg.Open()
	if err != nil {
		fmt.Println("error opening connection,", err)
		return
	}

	// Register the messageCreate func as a callback for MessageCreate events.
	dg.AddHandler(messageCreate)

	// Start http server
	go httpserver()

	// Wait here until CTRL-C or other term signal is received.
	fmt.Println("Bot is now running.  Press CTRL-C to exit.")
	sc := make(chan os.Signal, 1)
	signal.Notify(sc, syscall.SIGINT, syscall.SIGTERM, os.Interrupt, os.Kill)
	<-sc

	// Cleanly close down the Discord session.
	dg.Close()
}

func httpserver() {
	http.HandleFunc("/result-post", handleResultPost)
	http.HandleFunc("/bot-activation-state_change", handleBotActivationStateChangePost)
	log.Fatal(http.ListenAndServe(":8880", nil))
}

type result_struct struct {
	MatchId  int    `json:"match_id"`
	RoundId  int    `json:"round_id"`
	Bot_a    string `json:"bot1"`
	Bot_a_id int    `json:"bot1_id"`
	Bot_b    string `json:"bot2"`
	Bot_b_id int    `json:"bot2_id"`
	Winner   string `json:"winner"`
	Replay   string `json:"replay_file_download_url"`
}

func handleResultPost(w http.ResponseWriter, r *http.Request) {
	decoder := json.NewDecoder(r.Body)
	var result result_struct
	err := decoder.Decode(&result)
	if err != nil {
		panic(err)
	}

	if result.Bot_a == result.Winner {
		embed := &discordgo.MessageEmbed{
			Color:       11534336, // Red Colour
			Description: "Round [" + strconv.Itoa(result.RoundId) + "](https://ai-arena.net/rounds/" + strconv.Itoa(result.RoundId) + "/) - Match [" + strconv.Itoa(result.MatchId) + "](https://ai-arena.net/matches/" + strconv.Itoa(result.MatchId) + "/) - [**" + result.Bot_a + "**](https://ai-arena.net/bots/" + strconv.Itoa(result.Bot_a_id) + "/) vs [" + result.Bot_b + "](https://ai-arena.net/bots/" + strconv.Itoa(result.Bot_b_id) + "/) - [Download Replay](https://ai-arena.net" + result.Replay + ")",
		}
		dg.ChannelMessageSendEmbed("571643904869269515", embed)

	} else if result.Bot_b == result.Winner {
		embed := &discordgo.MessageEmbed{
			Color:       11534336, // Red Colour
			Description: "Round [" + strconv.Itoa(result.RoundId) + "](https://ai-arena.net/rounds/" + strconv.Itoa(result.RoundId) + "/) - Match [" + strconv.Itoa(result.MatchId) + "](https://ai-arena.net/matches/" + strconv.Itoa(result.MatchId) + "/) - [" + result.Bot_a + "](https://ai-arena.net/bots/" + strconv.Itoa(result.Bot_a_id) + "/) vs [**" + result.Bot_b + "**](https://ai-arena.net/bots/" + strconv.Itoa(result.Bot_b_id) + "/) - [Download Replay](https://ai-arena.net" + result.Replay + ")",
		}
		dg.ChannelMessageSendEmbed("571643904869269515", embed)

	}
	SetMeleeChampion()
}

type activation_state_change_struct struct {
	BotName  string `json:"bot_name"`
	BotId    int    `json:"bot_id"`
	IsActive bool   `json:"is_active"`
}

func handleBotActivationStateChangePost(w http.ResponseWriter, r *http.Request) {
	decoder := json.NewDecoder(r.Body)
	var result result_struct
	err := decoder.Decode(&result)
	if err != nil {
		panic(err)
	}
}

func messageCreate(s *discordgo.Session, m *discordgo.MessageCreate) {
	// Ignore all messages created by the bot itself
	if m.Author.ID == s.State.User.ID {
		return
	}

	SetBotAuthorRole(m.Author.ID)

	// Only process valid commands
	if len(m.Content) > 1 && m.Content[:1] == "!" {
		log.Print(m.Content)
		method := strings.Split(m.Content, " ")[0][1:]

		if method == "help" {
			helpReply := &discordgo.MessageEmbed{
				Color: 11534336, // Red Colour
				Title: "Commands",
				Description: "!stream - Shows Stream URL" +
					"\n!invite - Get a discord invite link." +
					"\n!top10 - Top 10 Ranked Bot.s" +
					"\n!bot <botname> - Shows Bot information." +
					"\n!refreshroles - Refresh Discord roles based on website user data (e.g. Bot Authors, Donators, etc)." +
					"\n!trello - Shows Trello board links." +
					"\n!gs or !gettingstarted - Shows getting started infos." +
					"\n!j or !join - Request the stream voice listener bot to join the voice channel." +
					"\n!l or !leave - Request the stream voice listener bot to leave the voice channel.",
				Timestamp: time.Now().Format(time.RFC3339),
			}
			s.ChannelMessageSendEmbed(m.ChannelID, helpReply)
		}

		if method == "stream" {
			s.ChannelMessageSend(m.ChannelID, "Stream URL: <https://www.twitch.tv/aiarenastream>")
		}

		if method == "top10" {
			MeleeTopTen(m.ChannelID)
		}

		if method == "bot" {
			// trim leading and trailing spaces
			params_str := strings.Trim(m.Content, " ")
			params := strings.Split(params_str, " ")
			if len(params) == 2 {
				BotInfo(params[1], m.ChannelID)
			} else {
				BotInfoUsage(m.ChannelID)
			}
		}

		if method == "trello" {
			s.ChannelMessageSend(m.ChannelID,
				"Trello boards:\n"+
					"General/misc: https://trello.com/b/ykMT2vyR/ai-arena-general\n"+
					"Website: https://trello.com/b/qw4DYU9H/ai-arena-website\n"+
					"Arena Client: https://trello.com/b/a7cUfzl0/ai-arena-client\n"+
					"Devop: https://trello.com/b/Tu2GR6gn/ai-arena-devop")
		}

		if method == "gs" || method == "gettingstarted" {
			s.ChannelMessageSend(m.ChannelID,
				"Getting started: https://ai-arena.net/wiki/bot-development/getting-started/")
		}

		if method == "invite" {
			s.ChannelMessageSend(m.ChannelID,
				"Discord invite link: https://discord.gg/yDBzbtC")
		}

		if method == "refreshroles" {
			RefreshAllBotAuthorRoles()
		}
	}
}

type BotInfoStruct struct {
	Name    string `json:"name"`
	Created string `json:"created"`
	Elo     int    `json:"elo"`
	Race    string `json:"plays_race"`
	Type    string `json:"type"`
	UserID  int    `json:"user_id"`
	BotID   int    `json:"id"`
}

type AuthorInfoStruct struct {
	Name string `json:"username"`
}

type AuthorAvatarStruct struct {
	Avatar string `json:"avatar"`
}

func BotInfoUsage(ChannelID string) {
	BotInfoReply := &discordgo.MessageEmbed{
		Color:       11534336,
		Title:       "!bot usage",
		Description: "!bot <bot_name>",
	}

	dg.ChannelMessageSendEmbed(ChannelID, BotInfoReply)
}

func BotInfo(botname string, ChannelID string) {
	is_valid_query, err := regexp.Match(`^[0-9a-zA-Z\._\-]*$`, []byte(botname))
	if err != nil {
		log.Print(err.Error())
	}

	// Ensure the query doesn't contain any invalid characters
	if is_valid_query {
		db, err := sql.Open("mysql", viper.GetString("MysqlUser")+":"+viper.GetString("MysqlPass")+"@tcp("+viper.GetString("MysqlHost")+")/"+viper.GetString("MysqlDB"))
		if err != nil {
			log.Print(err.Error())
		}
		defer db.Close()

		// First check whether there's an exact match. If there isn't, we'll try a partial match
		exact_match_count_results, err := db.Query("SELECT count(*) as exact_match_count FROM aiarena_beta.core_bot where name = ?", botname)
		if err != nil {
			panic(err.Error())
		}

		exact_match_count := 0
		for exact_match_count_results.Next() {
			err = exact_match_count_results.Scan(&exact_match_count)
			if err != nil {
				panic(err.Error())
			}
		}

		if exact_match_count == 1 {
			currentseasonid_results, err := db.Query("SELECT a.id FROM core_season a LEFT OUTER JOIN core_season b ON a.id = b.id AND a.number < b.number WHERE b.id IS NULL")
			if err != nil {
				panic(err.Error())
			}

			currentseasonid := 0
			for currentseasonid_results.Next() {
				err = currentseasonid_results.Scan(&currentseasonid)
				if err != nil {
					panic(err.Error())
				}
			}

			botresults, err := db.Query("SELECT name, created, elo, plays_race, type, user_id, b.id FROM aiarena_beta.core_seasonparticipation sp inner join aiarena_beta.core_bot b on sp.bot_id = b.id where name = ? and season_id = ?", botname, currentseasonid)
			if err != nil {
				panic(err.Error())
			}

			var botdata BotInfoStruct
			for botresults.Next() {
				err = botresults.Scan(&botdata.Name, &botdata.Created, &botdata.Elo, &botdata.Race, &botdata.Type, &botdata.UserID, &botdata.BotID)
				if err != nil {
					panic(err.Error())
				}
			}

			authorresults, err := db.Query("SELECT username FROM aiarena_beta.core_user where id = ?", &botdata.UserID)
			if err != nil {
				panic(err.Error())
			}

			var authordata AuthorInfoStruct
			for authorresults.Next() {
				err = authorresults.Scan(&authordata.Name)
				if err != nil {
					panic(err.Error())
				}
			}

			avatarresults, err := db.Query("SELECT avatar FROM aiarena_beta.avatar_avatar where user_id = ? and `primary` = 1", &botdata.UserID)
			if err != nil {
				panic(err.Error())
			}

			var avatardata AuthorAvatarStruct
			for avatarresults.Next() {
				err = avatarresults.Scan(&avatardata.Avatar)
				if err != nil {
					panic(err.Error())
				}
			}

			fullrace := "None"
			if botdata.Race == "R" {
				fullrace = "Random"
			} else if botdata.Race == "T" {
				fullrace = "Terran"
			} else if botdata.Race == "P" {
				fullrace = "Protoss"
			} else if botdata.Race == "Z" {
				fullrace = "Zerg"
			}
			BotInfoReply := &discordgo.MessageEmbed{
				Color:       11534336,
				Title:       botdata.Name,
				Description: "Author: " + authordata.Name + "\nRace: " + fullrace + "\nELO: " + strconv.Itoa(botdata.Elo) + "\nType: " + botdata.Type + "\n[Bot page](https://ai-arena.net/bots/" + strconv.Itoa(botdata.BotID) + ")",
				Thumbnail: &discordgo.MessageEmbedThumbnail{
					URL: "https://ai-arena.net/media/" + avatardata.Avatar,
				},
				Image: &discordgo.MessageEmbedImage{
					URL: "https://ai-arena.net/media/graphs/" + strconv.Itoa(currentseasonid) + "_" + strconv.Itoa(botdata.BotID) + "_" + botdata.Name + ".png?t=" + time.Now().Format("20060102150405"),
				},
			}

			dg.ChannelMessageSendEmbed(ChannelID, BotInfoReply)
		} else if exact_match_count > 1 {
			BotInfoReply := &discordgo.MessageEmbed{
				Color:       11534336,
				Title:       "Error",
				Description: "That's weird. Multiple bots matched that name exactly. This is an error. Kindly please let a staff member know.",
			}

			dg.ChannelMessageSendEmbed(ChannelID, BotInfoReply)
		} else { // No exact match found

			botname_len := len(botname)
			partial_match_count_results, err := db.Query("SELECT count(*) as partial_match_count FROM aiarena_beta.core_bot where LEFT(name, ?) = ?", botname_len, botname)
			if err != nil {
				panic(err.Error())
			}

			partial_match_count := 0
			for partial_match_count_results.Next() {
				err = partial_match_count_results.Scan(&partial_match_count)
				if err != nil {
					panic(err.Error())
				}
			}

			if partial_match_count == 1 { // dump that bot's info
				currentseasonid_results, err := db.Query("SELECT a.id FROM core_season a LEFT OUTER JOIN core_season b ON a.id = b.id AND a.number < b.number WHERE b.id IS NULL")
				if err != nil {
					panic(err.Error())
				}

				currentseasonid := 0
				for currentseasonid_results.Next() {
					err = currentseasonid_results.Scan(&currentseasonid)
					if err != nil {
						panic(err.Error())
					}
				}

				botresults, err := db.Query("SELECT name, created, elo, plays_race, type, user_id, b.id FROM aiarena_beta.core_seasonparticipation sp inner join aiarena_beta.core_bot b on sp.bot_id = b.id where LEFT(name, ?) = ? and season_id = ?", botname_len, botname, currentseasonid)
				if err != nil {
					panic(err.Error())
				}

				var botdata BotInfoStruct
				for botresults.Next() {
					err = botresults.Scan(&botdata.Name, &botdata.Created, &botdata.Elo, &botdata.Race, &botdata.Type, &botdata.UserID, &botdata.BotID)
					if err != nil {
						panic(err.Error())
					}
				}

				authorresults, err := db.Query("SELECT username FROM aiarena_beta.core_user where id = ?", &botdata.UserID)
				if err != nil {
					panic(err.Error())
				}

				var authordata AuthorInfoStruct
				for authorresults.Next() {
					err = authorresults.Scan(&authordata.Name)
					if err != nil {
						panic(err.Error())
					}
				}

				avatarresults, err := db.Query("SELECT avatar FROM aiarena_beta.avatar_avatar where user_id = ? and `primary` = 1", &botdata.UserID)
				if err != nil {
					panic(err.Error())
				}

				var avatardata AuthorAvatarStruct
				for avatarresults.Next() {
					err = avatarresults.Scan(&avatardata.Avatar)
					if err != nil {
						panic(err.Error())
					}
				}

				fullrace := "None"
				if botdata.Race == "R" {
					fullrace = "Random"
				} else if botdata.Race == "T" {
					fullrace = "Terran"
				} else if botdata.Race == "P" {
					fullrace = "Protoss"
				} else if botdata.Race == "Z" {
					fullrace = "Zerg"
				}

				BotInfoReply := &discordgo.MessageEmbed{
					Color:       11534336,
					Title:       botdata.Name,
					Description: "Author: " + authordata.Name + "\nRace: " + fullrace + "\nCreated: " + botdata.Created + "\nELO: " + strconv.Itoa(botdata.Elo) + "\nType: " + botdata.Type + "\n[Bot page](https://ai-arena.net/bots/" + strconv.Itoa(botdata.BotID) + ")",
					Thumbnail: &discordgo.MessageEmbedThumbnail{
						URL: "https://ai-arena.net/media/" + avatardata.Avatar,
					},
					Image: &discordgo.MessageEmbedImage{
						URL: "https://ai-arena.net/media/graphs/" + strconv.Itoa(currentseasonid) + "_" + strconv.Itoa(botdata.BotID) + "_" + botdata.Name + ".png?t=" + time.Now().Format("20060102150405"),
					},
				}

				dg.ChannelMessageSendEmbed(ChannelID, BotInfoReply)

			} else if partial_match_count > 1 {
				botresults, err := db.Query("SELECT name FROM aiarena_beta.core_bot where LEFT(name, ?) = ?", botname_len, botname)
				if err != nil {
					panic(err.Error())
				}

				bot_names_buffer := bytes.Buffer{}
				var bot_name string
				for botresults.Next() {
					err = botresults.Scan(&bot_name)
					if err != nil {
						panic(err.Error())
					}
					bot_names_buffer.WriteString(bot_name)
					bot_names_buffer.WriteString("\n")
				}

				BotInfoReply := &discordgo.MessageEmbed{
					Color:       11534336,
					Title:       "Multiple bots",
					Description: "That query returned multiple bots:\n" + bot_names_buffer.String(),
				}

				dg.ChannelMessageSendEmbed(ChannelID, BotInfoReply)

			} else {
				BotInfoReply := &discordgo.MessageEmbed{
					Color:       11534336,
					Title:       "No bots",
					Description: "Sorry, that query returned no matching bots.",
				}

				dg.ChannelMessageSendEmbed(ChannelID, BotInfoReply)
			}
		}
	} else {
		BotInfoReply := &discordgo.MessageEmbed{
			Color:       11534336,
			Title:       "Invalid query",
			Description: "Sorry, that query didn't make sense to me.\nAre you using invalid characters?",
		}

		dg.ChannelMessageSendEmbed(ChannelID, BotInfoReply)
	}

}

type ChampionStruct struct {
	UserID int `json:"user_id"`
}

type DiscordUserStruct struct {
	UserID int `json:"uid"`
}

func SetMeleeChampion() {
	db, err := sql.Open("mysql", viper.GetString("MysqlUser")+":"+viper.GetString("MysqlPass")+"@tcp("+viper.GetString("MysqlHost")+")/"+viper.GetString("MysqlDB"))
	if err != nil {
		log.Print(err.Error())
	}
	defer db.Close()

	currentseasonid_results, err := db.Query("SELECT a.id FROM core_season a LEFT OUTER JOIN core_season b ON a.id = b.id AND a.number < b.number WHERE b.id IS NULL")
	if err != nil {
		panic(err.Error())
	}

	currentseasonid := 0
	for currentseasonid_results.Next() {
		err = currentseasonid_results.Scan(&currentseasonid)
		if err != nil {
			panic(err.Error())
		}
	}

	meleechamionresult, err := db.Query("SELECT user_id FROM aiarena_beta.core_seasonparticipation sp inner join aiarena_beta.core_bot b on sp.bot_id = b.id where season_id = ? and active = 1 order by elo desc limit 1", currentseasonid)
	if err != nil {
		panic(err.Error())
	}

	var championdata ChampionStruct
	for meleechamionresult.Next() {
		err = meleechamionresult.Scan(&championdata.UserID)
		if err != nil {
			panic(err.Error())
		}
	}

	discordresult, err := db.Query("SELECT uid FROM aiarena_beta.discord_bind_discorduser where user_id = ?", &championdata.UserID)
	if err != nil {
		panic(err.Error())
	}

	var discorddata DiscordUserStruct
	for discordresult.Next() {
		err = discordresult.Scan(&discorddata.UserID)
		if err != nil {
			panic(err.Error())
		}
	}

	if discorddata.UserID != 0 {
		if discorddata.UserID != viper.GetInt("MeleeChampion") {
			if viper.GetInt("MeleeChampion") != 0 {
				remerr := dg.GuildMemberRoleRemove("430111136822722590", strconv.Itoa(viper.GetInt("MeleeChampion")), "630182770366349312")
				if remerr != nil {
					fmt.Println("Call to GuildMemberRoleRemove failed with parameter: " + strconv.Itoa(viper.GetInt("MeleeChampion")))
					fmt.Printf(remerr.Error())
				}
			}

			viper.Set("MeleeChampion", discorddata.UserID)
			viper.WriteConfig()

			adderr := dg.GuildMemberRoleAdd("430111136822722590", strconv.Itoa(discorddata.UserID), "630182770366349312")
			if adderr != nil {
				fmt.Println("Failed to assign Discord role to AI Arena user: " + strconv.Itoa(championdata.UserID))
				fmt.Printf(adderr.Error())
			}

			user, usrerr := dg.User(strconv.Itoa(discorddata.UserID))
			if usrerr != nil {
				panic(usrerr.Error())
			}

			dg.ChannelMessageSend("555377512012709898", "Congratulations "+user.Username+"! You are the Melee Ladder Champion!")
		}
	} else {
		if viper.GetInt("MeleeChampion") != 0 {
			remerr := dg.GuildMemberRoleRemove("430111136822722590", strconv.Itoa(viper.GetInt("MeleeChampion")), "630182770366349312")
			if remerr != nil {
				fmt.Println("Call to GuildMemberRoleRemove failed with parameter: " + strconv.Itoa(viper.GetInt("MeleeChampion")))
				fmt.Printf(remerr.Error())
			}

			viper.Set("MeleeChampion", 0)
			viper.WriteConfig()
		}
	}
}

type BotAuthorRoleStruct struct {
	UserID    int  `json:"user_id"`
	IsDonator bool `json:"is_donator"`
}

func RefreshAllBotAuthorRoles() {
	db, err := sql.Open("mysql", viper.GetString("MysqlUser")+":"+viper.GetString("MysqlPass")+"@tcp("+viper.GetString("MysqlHost")+")/"+viper.GetString("MysqlDB"))
	if err != nil {
		log.Print(err.Error())
	}
	defer db.Close()

	discordresult, err := db.Query("SELECT user_id, case patreon_level when 'none' then false else true end as is_donator FROM discord_bind_discorduser inner join core_user on discord_bind_discorduser.user_id = core_user.id", discordid)
	if err != nil {
		panic(err.Error())
	}

	var discorddata BotAuthorRoleStruct
	for discordresult.Next() {
		err = discordresult.Scan(&discorddata.UserID, &discorddata.IsDonator)
		if err != nil {
			log.Print(err.Error())
			continue
		}

		if discorddata.UserID != 0 {
			adderr := dg.GuildMemberRoleAdd("430111136822722590", strconv.Itoa(discorddata.UserID), "555372163788570635")
			if adderr != nil {
				log.Print(err.Error())
				continue
			}
			if discorddata.IsDonator {
				adderr := dg.GuildMemberRoleAdd("430111136822722590", strconv.Itoa(discorddata.UserID), "610982126669660218")
				if adderr != nil {
					log.Print(err.Error())
					continue
				}
			} else {
				adderr := dg.GuildMemberRoleRemove("430111136822722590", strconv.Itoa(discorddata.UserID), "610982126669660218")
				if adderr != nil {
					log.Print(err.Error())
					continue
				}
			}
		}
	}
}

func SetBotAuthorRole(discordid string) {
	db, err := sql.Open("mysql", viper.GetString("MysqlUser")+":"+viper.GetString("MysqlPass")+"@tcp("+viper.GetString("MysqlHost")+")/"+viper.GetString("MysqlDB"))
	if err != nil {
		log.Print(err.Error())
	}
	defer db.Close()

	discordresult, err := db.Query("SELECT user_id, case patreon_level when 'none' then false else true end as is_donator FROM discord_bind_discorduser inner join core_user on discord_bind_discorduser.user_id = core_user.id where uid = ?", discordid)
	if err != nil {
		panic(err.Error())
	}

	var discorddata BotAuthorRoleStruct
	for discordresult.Next() {
		err = discordresult.Scan(&discorddata.UserID, &discorddata.IsDonator)
		if err != nil {
			log.Print(err.Error())
			return
		}
	}

	if discorddata.UserID != 0 {
		adderr := dg.GuildMemberRoleAdd("430111136822722590", discordid, "555372163788570635")
		if adderr != nil {
			log.Print(err.Error())
			return
		}
		if discorddata.IsDonator {
			adderr := dg.GuildMemberRoleAdd("430111136822722590", discordid, "610982126669660218")
			if adderr != nil {
				log.Print(err.Error())
				return
			}
		} else {
			adderr := dg.GuildMemberRoleRemove("430111136822722590", discordid, "610982126669660218")
			if adderr != nil {
				log.Print(err.Error())
				return
			}
		}
	}
}

type TopTenStruct struct {
	Elo  int    `json:"elo"`
	Name string `json:"name"`
}

func MeleeTopTen(ChannelID string) {
	db, err := sql.Open("mysql", viper.GetString("MysqlUser")+":"+viper.GetString("MysqlPass")+"@tcp("+viper.GetString("MysqlHost")+")/"+viper.GetString("MysqlDB"))
	if err != nil {
		log.Print(err.Error())
	}
	defer db.Close()

	currentseasonid_results, err := db.Query("SELECT a.id FROM core_season a LEFT OUTER JOIN core_season b ON a.id = b.id AND a.number < b.number WHERE b.id IS NULL")
	if err != nil {
		panic(err.Error())
	}

	currentseasonid := 0
	for currentseasonid_results.Next() {
		err = currentseasonid_results.Scan(&currentseasonid)
		if err != nil {
			panic(err.Error())
		}
	}

	results, err := db.Query("SELECT name, elo FROM aiarena_beta.core_seasonparticipation sp inner join aiarena_beta.core_bot b on sp.bot_id = b.id where season_id = ? and active = 1 order by elo desc limit 10", currentseasonid)
	if err != nil {
		panic(err.Error())
	}

	place := 0
	list := []string{}
	for results.Next() {
		place++
		var data TopTenStruct
		err = results.Scan(&data.Name, &data.Elo)
		if err != nil {
			panic(err.Error())
		}
		list = append(list, "#"+strconv.Itoa(place)+" - "+data.Name+" - "+strconv.Itoa(data.Elo)+"\n")
	}

	MeleeTopTenReply := &discordgo.MessageEmbed{
		Color:       11534336,
		Title:       "Top 10 Bots on Melee Ladder",
		Description: strings.Join(list, " "),
		Timestamp:   time.Now().Format(time.RFC3339),
	}

	dg.ChannelMessageSendEmbed(ChannelID, MeleeTopTenReply)
}

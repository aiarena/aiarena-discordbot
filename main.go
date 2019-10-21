package main

import (
        "fmt"
        "os"
        "os/signal"
        "syscall"
        "log"
        "github.com/bwmarrin/discordgo"
        "net/http"
        "encoding/json"
        "time"
        "strings"
        "strconv"
        "github.com/spf13/viper"
        "database/sql"
        _ "github.com/go-sql-driver/mysql"
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
        log.Fatal(http.ListenAndServe(":8880", nil))
}

type result_struct struct {
        MatchId int `json:"match_id"`
        RoundId int `json:"round_id"`
        Bot_a string `json:"bot1"`
        Bot_a_id int `json:"bot1_id"`
        Bot_b string `json:"bot2"`
        Bot_b_id int `json:"bot2_id"`
        Winner string `json:"winner"`
        Replay string `json:"replay_file_download_url"`
}

func handleResultPost(w http.ResponseWriter, r *http.Request) {
        decoder := json.NewDecoder(r.Body)
        var result result_struct
        err := decoder.Decode(&result)
        if err != nil {
                panic(err)
        }

        if result.Bot_a == result.Winner {
                embed := &discordgo.MessageEmbed {
                        Color: 11534336, // Red Colour
                        Description: "Round [" + strconv.Itoa(result.RoundId) + "](https://ai-arena.net/rounds/" + strconv.Itoa(result.RoundId) + "/) - Match [" + strconv.Itoa(result.MatchId) + "](https://ai-arena.net/matches/" + strconv.Itoa(result.MatchId) + "/) - [**" + result.Bot_a + "**](https://ai-arena.net/bots/" + strconv.Itoa(result.Bot_a_id) + "/) vs [" + result.Bot_b + "](https://ai-arena.net/bots/" + strconv.Itoa(result.Bot_b_id) + "/) - [Download Replay](https://ai-arena.net" + result.Replay + ")",
                }
                dg.ChannelMessageSendEmbed("571643904869269515", embed)

        } else if result.Bot_b == result.Winner {
                embed := &discordgo.MessageEmbed {
                        Color: 11534336, // Red Colour
                        Description: "Round [" + strconv.Itoa(result.RoundId) + "](https://ai-arena.net/rounds/" + strconv.Itoa(result.RoundId) + "/) - Match [" + strconv.Itoa(result.MatchId) + "](https://ai-arena.net/matches/" + strconv.Itoa(result.MatchId) + "/) - [" + result.Bot_a + "](https://ai-arena.net/bots/" + strconv.Itoa(result.Bot_a_id) + "/) vs [**" + result.Bot_b + "**](https://ai-arena.net/bots/" + strconv.Itoa(result.Bot_b_id) + "/) - [Download Replay](https://ai-arena.net" + result.Replay + ")",
                }
                dg.ChannelMessageSendEmbed("571643904869269515", embed)

        }
        SetMeleeChampion()
}

func messageCreate(s *discordgo.Session, m *discordgo.MessageCreate) {
        // Ignore all messages created by the bot itself
        if m.Author.ID == s.State.User.ID {
                return
        }

        SetBotAuthorRole(m.Author.ID)

        if m.Content[:1] == "!" {
                method := strings.Split(m.Content, " ")[0][1:]

                if method == "help" {
                        helpReply := &discordgo.MessageEmbed {
                                Color: 11534336, // Red Colour
                                Title: "Commands",
                                Description: "!stream - Shows Stream URL\n!top10 - Top 10 Ranked Bots\n!bot <botname> - Shows Bot information\n!connectdiscord - Connects your discord account to the aiarena account",
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
                        param := strings.Split(m.Content, " ")[1]
                        BotInfo(param, m.ChannelID)
                }

		if method == "trello" {
			s.ChannelMessageSend(m.ChannelID,
				"Trello boards:\n" +
				"General/misc: [board](https://trello.com/b/ykMT2vyR/ai-arena-general)\n" +
				"Website: [board](https://trello.com/b/qw4DYU9H/ai-arena-website)\n" +
				"Arena Client: [board](https://trello.com/b/a7cUfzl0/ai-arena-client)\n" +
				"Devop: [board](https://trello.com/b/Tu2GR6gn/ai-arena-devop)")
		}
        }
}

type BotInfoStruct struct {
        Name string `json:"name"`
        Created string `json:"created"`
        Elo int `json:"elo"`
        Race string `json:"plays_race"`
        Type string `json:"type"`
        UserID int `json:"user_id"`
	BotID int `json:"id"`
}

type AuthorInfoStruct struct {
        Name string `json:"username"`
}

type AuthorAvatarStruct struct {
        Avatar string `json:"avatar"`
}

func BotInfo(botname string, ChannelID string) {
        db, err := sql.Open("mysql", viper.GetString("MysqlUser") + ":" + viper.GetString("MysqlPass") + "@tcp(" + viper.GetString("MysqlHost") + ")/" + viper.GetString("MysqlDB"))
        if err != nil {
                log.Print(err.Error())
        }
        defer db.Close()

        botresults, err := db.Query("SELECT name, created, elo, plays_race, type, user_id, id FROM aiarena_beta.core_bot where name = ?", botname)
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

        BotInfoReply := &discordgo.MessageEmbed {
                Color: 11534336,
                Title: botname,
                Description: "Author: " + authordata.Name  + "\nRace: " + fullrace + "\nCreated: " + botdata.Created + "\nELO: " + strconv.Itoa(botdata.Elo) + "\nType: " + botdata.Type,
                Thumbnail: &discordgo.MessageEmbedThumbnail{
                        URL: "https://ai-arena.net/media/" + avatardata.Avatar,
                },
                Image: &discordgo.MessageEmbedImage{
                        URL: "https://ai-arena.net/media/graphs/" + strconv.Itoa(botdata.BotID) + "_" + botdata.Name + ".png",
                },
        }

        dg.ChannelMessageSendEmbed(ChannelID, BotInfoReply)
}

type ChampionStruct struct {
        UserID int `json:"user_id"`
}

type DiscordUserStruct struct {
        UserID int `json:"uid"`
}

func SetMeleeChampion() {
        db, err := sql.Open("mysql", viper.GetString("MysqlUser") + ":" + viper.GetString("MysqlPass") + "@tcp(" + viper.GetString("MysqlHost") + ")/" + viper.GetString("MysqlDB"))
        if err != nil {
                log.Print(err.Error())
        }
        defer db.Close()

        meleechamionresult, err := db.Query("SELECT user_id FROM aiarena_beta.core_bot where active = 1 order by elo desc limit 1")
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
                        remerr := dg.GuildMemberRoleRemove("430111136822722590", strconv.Itoa(viper.GetInt("MeleeChampion")), "630182770366349312")
                        if remerr != nil {
                                panic(remerr.Error())
                        }

                        viper.Set("MeleeChampion", discorddata.UserID)
                        viper.WriteConfig()

                        adderr := dg.GuildMemberRoleAdd("430111136822722590", strconv.Itoa(discorddata.UserID), "630182770366349312")
                        if adderr != nil {
                                panic(adderr.Error())
                        }

                        user, usrerr := dg.User(strconv.Itoa(discorddata.UserID))
                        if usrerr != nil {
                                panic(usrerr.Error())
                        }

                        dg.ChannelMessageSend("555377512012709898", "Congratulations " + user.Username + "! You are the Melee Ladder Champion!")
                }
        } else {
		remerr := dg.GuildMemberRoleRemove("430111136822722590", strconv.Itoa(viper.GetInt("MeleeChampion")), "630182770366349312")
                if remerr != nil {
                        panic(remerr.Error())
                }

		viper.Set("MeleeChampion", "12345")
                viper.WriteConfig()
	}
}

type BotAuthorRoleStruct struct {
        UserID int `json:"user_id"`
}

func SetBotAuthorRole(discordid string) {
        db, err := sql.Open("mysql", viper.GetString("MysqlUser") + ":" + viper.GetString("MysqlPass") + "@tcp(" + viper.GetString("MysqlHost") + ")/" + viper.GetString("MysqlDB"))
        if err != nil {
                log.Print(err.Error())
        }
        defer db.Close()

        discordresult, err := db.Query("SELECT user_id FROM aiarena_beta.discord_bind_discorduser where uid = ?", discordid)
        if err != nil {
                panic(err.Error())
        }

        var discorddata BotAuthorRoleStruct
        for discordresult.Next() {
                err = discordresult.Scan(&discorddata.UserID)
                if err != nil {
                        panic(err.Error())
                }
        }

        if discorddata.UserID != 0 {
                adderr := dg.GuildMemberRoleAdd("430111136822722590", discordid, "555372163788570635")
                if adderr != nil {
                        panic(adderr.Error())
                }
        }
}

type TopTenStruct struct {
        Elo   int    `json:"elo"`
        Name  string `json:"name"`
}

func MeleeTopTen(ChannelID string) {
        db, err := sql.Open("mysql", viper.GetString("MysqlUser") + ":" + viper.GetString("MysqlPass") + "@tcp(" + viper.GetString("MysqlHost") + ")/" + viper.GetString("MysqlDB"))
        if err != nil {
                log.Print(err.Error())
        }
        defer db.Close()

        results, err := db.Query("SELECT name,elo FROM aiarena_beta.core_bot where active = 1 order by elo desc limit 10")
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
                list = append(list, "#" + strconv.Itoa(place) + " - " + data.Name + " - " + strconv.Itoa(data.Elo) + "\n")
        }

        MeleeTopTenReply := &discordgo.MessageEmbed {
                Color: 11534336,
                Title: "Top 10 Bots on Melee Ladder",
                Description: strings.Join(list, " "),
                Timestamp: time.Now().Format(time.RFC3339),
        }

        dg.ChannelMessageSendEmbed(ChannelID, MeleeTopTenReply)
}

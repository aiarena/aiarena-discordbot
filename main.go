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
        "github.com/tkanos/gonfig"
        "database/sql"
        _ "github.com/go-sql-driver/mysql"
)

// Config file handling
type Configuration struct {
        WebServerPort     string
        DiscordBotToken   string
        MysqlHost         string
        MysqlUser         string
        MysqlPass         string
        MysqlDB           string
        TwitchClientID    string
}
var configuration = Configuration{}
var err = gonfig.GetConf("config.json", &configuration)

const (
        EXIT_COMMAND = "exit"
)

// Make discord session globally available
var dg *discordgo.Session

func main() {
        var err error
        dg, err = discordgo.New("Bot " + configuration.DiscordBotToken)
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
        Id int `json:"match_id"`
        Bot_a string `json:"bot1"`
        Bot_b string `json:"bot2"`
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

        embed := &discordgo.MessageEmbed {
                Color: 11534336, // Red Colour
                Title: "#" + strconv.Itoa(result.Id),
                Description: "[" + result.Bot_a + " vs " + result.Bot_b + "](https://ai-arena.net/matches/" + strconv.Itoa(result.Id) + "/)\n**Winner:** " + result.Winner + "\n\n[Download Replay](https://ai-arena.net" + result.Replay + ")",
                Timestamp: time.Now().Format(time.RFC3339),
        }

        dg.ChannelMessageSendEmbed("571643904869269515", embed)
}

// This function will be called (due to AddHandler above) every time a new
// message is created on any channel that the autenticated bot has access to.
func messageCreate(s *discordgo.Session, m *discordgo.MessageCreate) {
        // Ignore all messages created by the bot itself
        if m.Author.ID == s.State.User.ID {
                return
        }

        if m.Content == "!help" {
                helpReply := &discordgo.MessageEmbed {
                        Color: 11534336, // Red Colour
                        Title: "Commands",
                        Description: "!stream - Shows Stream URL\n!top10 - Top 10 Ranked Bots\n!botinfo <botname> - Shows Bot information\n!connectdiscord - Connects your discord account to the aiarena account",
                        Timestamp: time.Now().Format(time.RFC3339),
                }
                s.ChannelMessageSendEmbed(m.ChannelID, helpReply)
        }

        if m.Content == "!stream" {
                s.ChannelMessageSend(m.ChannelID, "Stream URL: <https://www.twitch.tv/aiarenastream>")
        }

        if m.Content == "!top10" {
                TopTen(m.ChannelID)
        }

        // ToDo: Add parameter (botname)
        // ToDo: Add API Connection
        if m.Content == "!botinfo" {
                s.ChannelMessageSend(m.ChannelID, "<Botname> <Rank> <ELO> <last result>")
        }

        // ToDo: Login function
        // ToDo: SQL Connection
        if m.Content == "!rankme" {
                s.ChannelMessageSend(m.ChannelID, "Setting your Discord Rank...")
        }
}

type TopTenStruct struct {
    Elo   int    `json:"elo"`
    Name  string `json:"name"`
}

func TopTen(ChannelID string) {
        db, err := sql.Open("mysql", configuration.MysqlUser + ":" + configuration.MysqlPass + "@tcp(" + configuration.MysqlHost + ")/" + configuration.MysqlDB)
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

        TopTenReply := &discordgo.MessageEmbed {
                Color: 11534336,
                Title: "Top 10 Bots on Melee Ladder",
                Description: strings.Join(list, " "),
                Timestamp: time.Now().Format(time.RFC3339),
        }

        dg.ChannelMessageSendEmbed(ChannelID, TopTenReply)
}
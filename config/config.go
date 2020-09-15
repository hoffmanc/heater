package main

import (
	"bufio"
	"encoding/json"
	"fmt"
	"io"
	"io/ioutil"
	"os"
	"time"

	"github.com/gin-gonic/gin"
)

type AuthCreds struct {
	Username string `json:"username"`
	Password string `json:"password"`
}

func check(c *gin.Context, e error) {
	if e != nil {
		c.HTML(500, "config.tmpl", gin.H{"err": e})
		panic(e)
	}
}

func log() ([]byte, error) {
	fname := fmt.Sprintf("../log/%s.log", time.Now().Format("2006-01-02"))
	log.Println(fname)
	fh, err := os.Open(fname)
	if err != nil {
		return []byte{}, err
	}

	reader := bufio.NewReader(fh)
	var l []byte
	for {
		line, _, err := reader.ReadLine()
		if err == io.EOF {
			break
		} else if err != nil {
			return []byte{}, err
		}
		l = line
	}
	return l, nil
}

func readTemp(c *gin.Context) {
	log, err := log()
	check(c, err)
	tempConf, err := ioutil.ReadFile("temp.conf")
	check(c, err)
	c.HTML(200, "config.tmpl", gin.H{"temp": string(tempConf), "log": string(log)})
}

func getCreds(creds *AuthCreds) error {
	if credsTxt, err := ioutil.ReadFile(os.Getenv("AUTH_CREDS")); err != nil {
		return err
	} else {
		if err := json.Unmarshal(credsTxt, &creds); err != nil {
			return err
		}
	}
	return nil
}

func main() {
	r := gin.Default()
	r.LoadHTMLFiles("config.tmpl")

	var creds AuthCreds
	if err := getCreds(&creds); err != nil {
		panic(err)
	}

	log.Println(creds)

	authorized := r.Group("/", gin.BasicAuth(gin.Accounts{creds.Username: creds.Password}))

	authorized.GET("/config", readTemp)

	authorized.POST("/config", func(c *gin.Context) {
		err := ioutil.WriteFile("temp.conf", []byte(c.PostForm("newTemp")), 0664)
		check(c, err)
		readTemp(c)
	})

	r.Run(":8080")
}

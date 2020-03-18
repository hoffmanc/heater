package main

import (
	"encoding/json"
	"io/ioutil"
	"log"
	"os"

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

func readTemp(c *gin.Context) {
	dat, err := ioutil.ReadFile("temp.conf")
	check(c, err)
	c.HTML(200, "config.tmpl", gin.H{"temp": string(dat)})
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

package main

import (
	"bufio"
	"encoding/json"
	"fmt"
	"io"
	"io/ioutil"
	"log"
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

func readLog() ([]byte, error) {
	fname := fmt.Sprintf("../log/log-%s.log", time.Now().Format("2006-01-02"))
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

func status(c *gin.Context) {
	l, err := readLog()
	check(c, err)
	tempConf, err := ioutil.ReadFile("temp.conf")
	check(c, err)
	threshold, err := ioutil.ReadFile("threshold.conf")
	check(c, err)
	c.HTML(200, "config.tmpl", gin.H{"temp": string(tempConf), "threshold": string(threshold), "log": string(l)})
}

func setConf(c *gin.Context) {
	err := ioutil.WriteFile("threshold.conf", []byte(c.PostForm("newThreshold")), 0664)
	check(c, err)
	err = ioutil.WriteFile("temp.conf", []byte(c.PostForm("newTemp")), 0664)
	check(c, err)
	c.Redirect(302, "/config")
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

	authorized := r.Group("/")
	if os.Getenv("AUTH_CREDS") != "" {
		var creds AuthCreds
		if err := getCreds(&creds); err != nil {
			panic(err)
		}

		authorized = r.Group("/", gin.BasicAuth(gin.Accounts{creds.Username: creds.Password}))
	}
	authorized.GET("/config", status)
	authorized.POST("/config", setConf)
	r.Run(":8080")
}

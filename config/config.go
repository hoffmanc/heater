package main

import (
	"io/ioutil"

	"github.com/gin-gonic/gin"
)

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

func main() {
	r := gin.Default()
	r.LoadHTMLFiles("config.tmpl")

	r.GET("/config", readTemp)

	r.POST("/config", func(c *gin.Context) {
		err := ioutil.WriteFile("temp.conf", []byte(c.PostForm("newTemp")), 0664)
		check(c, err)
		readTemp(c)
	})
	r.Run(":8080")
}

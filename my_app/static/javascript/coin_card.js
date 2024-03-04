Vue.component('coin-card', {
    props: ['coin'],
    template: `
        <a class='nounderline' :href="'/coin/' + coin.symbol">
            <div class="coin-card-wrapper">
                <div class='coin-card-image-wrapper'>
                    <img class='coin-card-image' :src="coin.image_url"></img>
                </div>
                <div class='coin-card-text'>
                    <h2>[[ coin.name ]]</h2>
                    <h2>[[ coin.symbol ]]</h2>
                    <h3>[[ coin.price ]] <span class='currency'>AUD</span></h3>
                    <h4 :style="coin.percent_change_24h > 0 ? 'color:green' : 'color:red'">[[ coin.percent_change_24h > 0 ? '+' + coin.percent_change_24h : coin.percent_change_24h ]]%</h4>
                </div>
            </div>
        </a>
    `,
    delimiters: ["[[", "]]"]
})
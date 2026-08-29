;(function(global){
// Normalized phrases
const phrases = [
  {
    "scene": "diningFood",
    "sentence": "I'd like to make a reservation for two.",
    "note": "我想预订两人位。"
  },
  {
    "scene": "diningFood",
    "sentence": "What do you recommend?",
    "note": "你有什么推荐？"
  },
  {
    "scene": "diningFood",
    "sentence": "Could I have the check, please?",
    "note": "请给我账单好吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'm allergic to peanuts.",
    "note": "我对花生过敏。"
  },
  {
    "scene": "diningFood",
    "sentence": "Let's split the bill.",
    "note": "我们分开付账吧。"
  },
  {
    "scene": "diningFood",
    "sentence": "Table for four, please.",
    "note": "请安排四人桌。"
  },
  {
    "scene": "diningFood",
    "sentence": "Is this dish spicy?",
    "note": "这道菜辣吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "Could I see the wine list?",
    "note": "我能看看酒单吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'll have the same as him.",
    "note": "我要和他一样的。"
  },
  {
    "scene": "diningFood",
    "sentence": "This tastes delicious!",
    "note": "这个很好吃！"
  },
  {
    "scene": "diningFood",
    "sentence": "Could we have a booth by the window?",
    "note": "我们能要一个靠窗的卡座吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'd like my steak medium rare.",
    "note": "我的牛排要三分熟。"
  },
  {
    "scene": "diningFood",
    "sentence": "Is service included in the bill?",
    "note": "账单包含服务费吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "Could I get this to go?",
    "note": "这个可以打包吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "What are the specials today?",
    "note": "今天的特色菜是什么？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'm a vegetarian.",
    "note": "我是素食者。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could we have some more bread?",
    "note": "我们能再要些面包吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "This isn't what I ordered.",
    "note": "这不是我点的菜。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could I have some ice water?",
    "note": "能给我一些冰水吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "The food is taking too long.",
    "note": "食物上得太慢了。"
  },
  {
    "scene": "diningFood",
    "sentence": "I'd like to cancel my order.",
    "note": "我想取消我的订单。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you warm this up?",
    "note": "能把这个加热一下吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "Do you have any vegan options?",
    "note": "你们有纯素食选择吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'll have the soup of the day.",
    "note": "我要今日例汤。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could we get separate checks?",
    "note": "我们能分开结账吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "What's in this dish?",
    "note": "这道菜里有什么？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'd like to order dessert.",
    "note": "我想点甜点。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could I have a doggy bag?",
    "note": "能给我一个打包袋吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "Is the tap water safe to drink?",
    "note": "自来水可以安全饮用吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'm full, thank you.",
    "note": "我吃饱了，谢谢。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could I have the daily special?",
    "note": "我能要今日特价菜吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'd like my eggs scrambled.",
    "note": "我的鸡蛋要炒的。"
  },
  {
    "scene": "diningFood",
    "sentence": "Is this made with fresh ingredients?",
    "note": "这是用新鲜食材做的吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you bring some extra napkins?",
    "note": "能再拿些餐巾纸吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "What's the house specialty?",
    "note": "你们的招牌菜是什么？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'll have the chef's recommendation.",
    "note": "我要主厨推荐。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could I substitute fries for salad?",
    "note": "我能把薯条换成沙拉吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "Is there a children's menu?",
    "note": "有儿童菜单吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'd like to try the local cuisine.",
    "note": "我想尝尝当地美食。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you recommend a good wine pairing?",
    "note": "你能推荐一款搭配的葡萄酒吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "Is this gluten-free?",
    "note": "这个是无麸质的吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'll have coffee with dessert.",
    "note": "甜点我要配咖啡。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could we have some more time to decide?",
    "note": "能多给我们些时间决定吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "What's the soup of the day?",
    "note": "今日例汤是什么？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'd like to order an appetizer.",
    "note": "我想点个开胃菜。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you make it less salty?",
    "note": "能做淡一点吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "Is the fish fresh today?",
    "note": "今天的鱼新鲜吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'll have the set menu.",
    "note": "我要套餐。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you tell me about this dish?",
    "note": "你能介绍一下这道菜吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "Is there a dress code?",
    "note": "有着装要求吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'd like to book a private room.",
    "note": "我想预订包间。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could we have some background music?",
    "note": "能放些背景音乐吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "What time does the kitchen close?",
    "note": "厨房什么时候关门？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'll have the breakfast buffet.",
    "note": "我要早餐自助餐。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you bring some hot sauce?",
    "note": "能拿些辣酱来吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "Is outdoor seating available?",
    "note": "有室外座位吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'd like to order takeout.",
    "note": "我想点外卖。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you recommend a good local beer?",
    "note": "你能推荐一款好的本地啤酒吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "Is the portion size large?",
    "note": "分量大吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'll have whatever you think is best.",
    "note": "我要你觉得最好的。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could we have some more water?",
    "note": "能再给我们些水吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "What would you like for dinner?",
    "note": "你晚饭想吃什么？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'm in the mood for some Italian food.",
    "note": "我想吃意大利菜。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you pass me the salt, please?",
    "note": "请把盐递给我好吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "This dish is a bit too spicy for me.",
    "note": "这道菜对我来说有点太辣了。"
  },
  {
    "scene": "diningFood",
    "sentence": "Is the service charge included?",
    "note": "服务费包含在内吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "This tastes delicious!",
    "note": "这个尝起来很好吃！"
  },
  {
    "scene": "diningFood",
    "sentence": "Are you ready to order?",
    "note": "您准备好点餐了吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'd like a table for two, please.",
    "note": "我想要一张两人桌。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could we have the menu, please?",
    "note": "请给我们菜单好吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "Is this dish vegetarian?",
    "note": "这道菜是素食吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "No onions for me, please.",
    "note": "请不要给我加洋葱。"
  },
  {
    "scene": "diningFood",
    "sentence": "The food here is amazing.",
    "note": "这里的食物太棒了。"
  },
  {
    "scene": "diningFood",
    "sentence": "Check, please.",
    "note": "买单。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could we have the dessert menu?",
    "note": "我们能看看甜点菜单吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'd like to try the tasting menu.",
    "note": "我想尝试品尝菜单。"
  },
  {
    "scene": "diningFood",
    "sentence": "Is this dish made to order?",
    "note": "这道菜是现做的吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "Could I have a glass of red wine?",
    "note": "我能要一杯红酒吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "What's the chef's special today?",
    "note": "今天的主厨特餐是什么？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'd like my steak well-done.",
    "note": "我的牛排要全熟。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you bring some lemon wedges?",
    "note": "能拿些柠檬角吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "Is there a corkage fee?",
    "note": "有开瓶费吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'll have the lunch special.",
    "note": "我要午餐特价菜。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you make it extra spicy?",
    "note": "能做特别辣吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "Is the seafood fresh today?",
    "note": "今天的海鲜新鲜吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'd like to order a cocktail.",
    "note": "我想点一杯鸡尾酒。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you recommend a non-alcoholic drink?",
    "note": "你能推荐一款无酒精饮料吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "Is there a happy hour?",
    "note": "有欢乐时光吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'll have a bottle of mineral water.",
    "note": "我要一瓶矿泉水。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you bring some soy sauce?",
    "note": "能拿些酱油吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "What's the spiciest dish you have?",
    "note": "你们最辣的菜是什么？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'd like to order some tapas.",
    "note": "我想点些西班牙小菜。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could we have a high chair for the baby?",
    "note": "能给我们宝宝一张高脚椅吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "Is this restaurant family-friendly?",
    "note": "这家餐厅适合家庭吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'll have the seafood platter.",
    "note": "我要海鲜拼盘。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you bring some toothpicks?",
    "note": "能拿些牙签吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "What's the most popular dish?",
    "note": "最受欢迎的菜是什么？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'd like to order the chef's tasting menu.",
    "note": "我想点主厨品尝菜单。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you make it without garlic?",
    "note": "能做不含大蒜的吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "Is the meat organic?",
    "note": "这肉是有机的吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'll have the grilled vegetables.",
    "note": "我要烤蔬菜。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you bring some chili oil?",
    "note": "能拿些辣椒油吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "What's the soup base for this dish?",
    "note": "这道菜的汤底是什么？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'd like to order some sushi.",
    "note": "我想点些寿司。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could we have a quiet table?",
    "note": "我们能要一个安静的桌子吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "Is there a buffet option?",
    "note": "有自助餐选项吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'll have the pasta with white sauce.",
    "note": "我要白酱意大利面。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you bring some grated cheese?",
    "note": "能拿些碎奶酪吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "What's the best dish for sharing?",
    "note": "最适合分享的菜是什么？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'd like to order the surf and turf.",
    "note": "我想点海陆大餐。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you make it with less oil?",
    "note": "能做少油一点吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "Is the chicken free-range?",
    "note": "这是散养鸡吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'll have the fish and chips.",
    "note": "我要炸鱼薯条。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you bring some tartar sauce?",
    "note": "能拿些塔塔酱吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "What's the signature cocktail?",
    "note": "招牌鸡尾酒是什么？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'd like to order the brunch menu.",
    "note": "我想点早午餐菜单。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you make it without MSG?",
    "note": "能做不含味精的吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "Is the beef grass-fed?",
    "note": "这是草饲牛肉吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'll have the chicken curry.",
    "note": "我要咖喱鸡。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you bring some naan bread?",
    "note": "能拿些印度烤饼吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "What's the best dessert here?",
    "note": "这里最好的甜点是什么？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'd like to order the afternoon tea.",
    "note": "我想点下午茶。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you make it with brown rice?",
    "note": "能做糙米饭吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "Is the salmon wild-caught?",
    "note": "这是野生鲑鱼吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'll have the vegetable stir-fry.",
    "note": "我要蔬菜炒菜。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you bring some oyster sauce?",
    "note": "能拿些蚝油吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "What's the best appetizer to start with?",
    "note": "最好先点什么开胃菜？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'd like to order the seafood paella.",
    "note": "我想点海鲜烩饭。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you make it without cilantro?",
    "note": "能做不含香菜的吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "Is the duck locally sourced?",
    "note": "这是本地鸭吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'll have the lamb chops.",
    "note": "我要羊排。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you bring some mint sauce?",
    "note": "能拿些薄荷酱吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "What's the best wine to pair with steak?",
    "note": "配牛排最好的葡萄酒是什么？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'd like to order the cheese platter.",
    "note": "我想点奶酪拼盘。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you make it with whole wheat bread?",
    "note": "能做全麦面包吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "Is the pork hormone-free?",
    "note": "这是无激素猪肉吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'll have the beef brisket.",
    "note": "我要牛腩。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you bring some barbecue sauce?",
    "note": "能拿些烧烤酱吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "What's the best dish for someone who doesn't eat meat?",
    "note": "不吃肉的人最好点什么菜？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'd like to order the fondue.",
    "note": "我想点火锅。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you make it with gluten-free pasta?",
    "note": "能做无麸质意大利面吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "Is the produce organic?",
    "note": "农产品是有机的吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'll have the mushroom risotto.",
    "note": "我要蘑菇烩饭。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you bring some truffle oil?",
    "note": "能拿些松露油吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "What's the best dish for a first-time visitor?",
    "note": "第一次来的客人最好点什么菜？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'd like to order the charcuterie board.",
    "note": "我想点冷肉拼盘。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you make it with low sodium?",
    "note": "能做低钠的吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "Is the fish sustainably caught?",
    "note": "这是可持续捕捞的鱼吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'll have the duck confit.",
    "note": "我要油封鸭。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you bring some orange sauce?",
    "note": "能拿些橙酱吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "What's the best dish for a cold day?",
    "note": "冷天最好点什么菜？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'd like to order the bouillabaisse.",
    "note": "我想点马赛鱼汤。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you make it with less sugar?",
    "note": "能做少糖一点吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "Is the bread baked fresh daily?",
    "note": "面包是每天新鲜烤的吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'll have the pumpkin soup.",
    "note": "我要南瓜汤。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you bring some croutons?",
    "note": "能拿些面包丁吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "What's the best dish for a hot day?",
    "note": "热天最好点什么菜？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'd like to order the gazpacho.",
    "note": "我想点西班牙凉汤。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you make it with almond milk?",
    "note": "能做杏仁奶的吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "Is the ice made from filtered water?",
    "note": "冰是用过滤水做的吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'll have the fruit salad.",
    "note": "我要水果沙拉。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you bring some honey?",
    "note": "能拿些蜂蜜吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "What's the best dish for someone on a diet?",
    "note": "节食的人最好点什么菜？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'd like to order the quinoa bowl.",
    "note": "我想点藜麦碗。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you make it with coconut oil?",
    "note": "能做椰子油的吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "Is the honey local?",
    "note": "这是本地蜂蜜吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'll have the avocado toast.",
    "note": "我要牛油果吐司。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you bring some chili flakes?",
    "note": "能拿些辣椒片吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "What's the best dish for someone who loves spicy food?",
    "note": "爱吃辣的人最好点什么菜？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'd like to order the vindaloo.",
    "note": "我想点文达卢咖喱。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you make it with extra chili?",
    "note": "能做额外加辣椒的吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "Is the spice level adjustable?",
    "note": "辣度可以调整吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'll have the pad thai.",
    "note": "我要泰式炒河粉。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you bring some peanuts?",
    "note": "能拿些花生吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "What's the best dish for someone who doesn't like spicy food?",
    "note": "不爱吃辣的人最好点什么菜？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'd like to order the chicken noodle soup.",
    "note": "我想点鸡肉面条汤。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you make it mild?",
    "note": "能做微辣的吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "Is the broth made from scratch?",
    "note": "汤底是现熬的吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'll have the pho.",
    "note": "我要越南河粉。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you bring some bean sprouts?",
    "note": "能拿些豆芽吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "What's the best dish for someone who loves seafood?",
    "note": "爱吃海鲜的人最好点什么菜？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'd like to order the lobster bisque.",
    "note": "我想点龙虾浓汤。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you make it with extra cream?",
    "note": "能做额外加奶油的吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "Is the lobster fresh or frozen?",
    "note": "龙虾是新鲜的还是冷冻的？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'll have the crab cakes.",
    "note": "我要蟹饼。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you bring some remoulade sauce?",
    "note": "能拿些雷莫拉酱吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "What's the best dish for someone who loves meat?",
    "note": "爱吃肉的人最好点什么菜？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'd like to order the tomahawk steak.",
    "note": "我想点战斧牛排。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you make it with a red wine reduction?",
    "note": "能做红酒汁的吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "Is the steak aged?",
    "note": "牛排是熟成的吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'll have the ribs.",
    "note": "我要肋排。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you bring some wet wipes?",
    "note": "能拿些湿巾吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "What's the best dish for someone who loves cheese?",
    "note": "爱吃奶酪的人最好点什么菜？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'd like to order the four-cheese pizza.",
    "note": "我想点四奶酪披萨。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you make it with extra cheese?",
    "note": "能做额外加奶酪的吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "Is the cheese imported?",
    "note": "奶酪是进口的吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'll have the mac and cheese.",
    "note": "我要通心粉和奶酪。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you bring some breadcrumbs?",
    "note": "能拿些面包屑吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "What's the best dish for someone with a sweet tooth?",
    "note": "爱吃甜食的人最好点什么菜？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'd like to order the chocolate lava cake.",
    "note": "我想点巧克力熔岩蛋糕。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you make it with vanilla ice cream?",
    "note": "能做香草冰淇淋的吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "Is the chocolate fair trade?",
    "note": "这是公平贸易巧克力吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'll have the cheesecake.",
    "note": "我要芝士蛋糕。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you bring some berry compote?",
    "note": "能拿些浆果蜜饯吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "What's the best dish for someone who loves coffee?",
    "note": "爱喝咖啡的人最好点什么菜？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'd like to order the tiramisu.",
    "note": "我想点提拉米苏。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you make it with decaf espresso?",
    "note": "能做无咖啡因浓缩咖啡的吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "Is the coffee single-origin?",
    "note": "这是单一产地咖啡吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'll have the affogato.",
    "note": "我要阿芙佳朵。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you bring some biscotti?",
    "note": "能拿些意式脆饼吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "What's the best dish for someone who loves tea?",
    "note": "爱喝茶的人最好点什么菜？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'd like to order the matcha latte.",
    "note": "我想点抹茶拿铁。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you make it with oat milk?",
    "note": "能做燕麦奶的吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "Is the tea loose leaf?",
    "note": "这是散装茶叶吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'll have the chai tea.",
    "note": "我要印度奶茶。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you bring some honey and milk?",
    "note": "能拿些蜂蜜和牛奶吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "What's the best dish for someone who loves breakfast food?",
    "note": "爱吃早餐食品的人最好点什么菜？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'd like to order the eggs benedict.",
    "note": "我想点班尼迪克蛋。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you make it with smoked salmon?",
    "note": "能做烟熏三文鱼的吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "Is the hollandaise sauce homemade?",
    "note": "荷兰酱是自制的吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'll have the french toast.",
    "note": "我要法式吐司。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you bring some maple syrup?",
    "note": "能拿些枫糖浆吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "What's the best dish for someone who loves burgers?",
    "note": "爱吃汉堡的人最好点什么菜？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'd like to order the wagyu burger.",
    "note": "我想点和牛汉堡。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you make it with a gluten-free bun?",
    "note": "能做无麸质面包的吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "Is the beef ground fresh daily?",
    "note": "牛肉是每天新鲜绞的吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'll have the pulled pork sandwich.",
    "note": "我要手撕猪肉三明治。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you bring some coleslaw?",
    "note": "能拿些凉拌卷心菜吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "What's the best dish for someone who loves pasta?",
    "note": "爱吃意大利面的人最好点什么菜？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'd like to order the carbonara.",
    "note": "我想点卡邦尼意大利面。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you make it with guanciale?",
    "note": "能做猪面颊肉的吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "Is the pasta homemade?",
    "note": "意大利面是自制的吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'll have the lasagna.",
    "note": "我要千层面。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you bring some garlic bread?",
    "note": "能拿些蒜香面包吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "What's the best dish for someone who loves soup?",
    "note": "爱喝汤的人最好点什么菜？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'd like to order the French onion soup.",
    "note": "我想点法式洋葱汤。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you make it with vegetable broth?",
    "note": "能做蔬菜汤底的嘛？"
  },
  {
    "scene": "diningFood",
    "sentence": "Is the soup served with bread?",
    "note": "汤配面包吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'll have the minestrone.",
    "note": "我要蔬菜通心粉汤。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you bring some parmesan cheese?",
    "note": "能拿些帕尔马奶酪吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "What's the best dish for someone who loves salad?",
    "note": "爱吃沙拉的人最好点什么菜？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'd like to order the Caesar salad.",
    "note": "我想点凯撒沙拉。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you make it without anchovies?",
    "note": "能做不含凤尾鱼的嘛？"
  },
  {
    "scene": "diningFood",
    "sentence": "Is the dressing on the side?",
    "note": "酱料是分开的嘛？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'll have the Greek salad.",
    "note": "我要希腊沙拉。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you bring some olive oil and vinegar?",
    "note": "能拿些橄榄油和醋吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "What's the best dish for someone who loves Asian food?",
    "note": "爱吃亚洲菜的人最好点什么菜？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'd like to order the chicken teriyaki.",
    "note": "我想点照烧鸡。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you make it with extra vegetables?",
    "note": "能做额外加蔬菜的嘛？"
  },
  {
    "scene": "diningFood",
    "sentence": "Is the rice white or brown?",
    "note": "是白米饭还是糙米饭？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'll have the beef and broccoli.",
    "note": "我要牛肉西兰花。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you bring some steamed rice?",
    "note": "能拿些白米饭吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "What's the best dish for someone who loves Mexican food?",
    "note": "爱吃墨西哥菜的人最好点什么菜？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'd like to order the chicken fajitas.",
    "note": "我想点鸡肉法士达。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you make it with corn tortillas?",
    "note": "能做玉米饼的嘛？"
  },
  {
    "scene": "diningFood",
    "sentence": "Is the guacamole made fresh?",
    "note": "鳄梨酱是新鲜做的嘛？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'll have the enchiladas.",
    "note": "我要辣酱玉米饼馅。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you bring some sour cream?",
    "note": "能拿些酸奶油吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "What's the best dish for someone who loves Indian food?",
    "note": "爱吃印度菜的人最好点什么菜？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'd like to order the butter chicken.",
    "note": "我想点奶油鸡。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you make it with less cream?",
    "note": "能做少奶油的嘛？"
  },
  {
    "scene": "diningFood",
    "sentence": "Is the naan baked in a tandoor?",
    "note": "烤饼是在泥炉里烤的嘛？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'll have the vegetable biryani.",
    "note": "我要蔬菜印度香饭。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you bring some raita?",
    "note": "能拿些印度酸奶酱吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "What's the best dish for someone who loves Mediterranean food?",
    "note": "爱吃地中海菜的人最好点什么菜？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'd like to order the grilled octopus.",
    "note": "我想点烤章鱼。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you make it with lemon and oregano?",
    "note": "能做柠檬和牛至的吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "Is the olive oil extra virgin?",
    "note": "这是特级初榨橄榄油吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'll have the moussaka.",
    "note": "我要慕萨卡。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you bring some tzatziki?",
    "note": "能拿些希腊酸奶黄瓜酱吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "What's the best dish for someone who loves barbecue?",
    "note": "爱吃烧烤的人最好点什么菜？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'd like to order the smoked brisket.",
    "note": "我想点熏牛腩。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you make it with a dry rub?",
    "note": "能做干腌料的嘛？"
  },
  {
    "scene": "diningFood",
    "sentence": "Is the barbecue sauce homemade?",
    "note": "烧烤酱是自制的嘛？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'll have the pulled chicken.",
    "note": "我要手撕鸡肉。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you bring some pickles?",
    "note": "能拿些腌黄瓜吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "What's the best dish for someone who loves comfort food?",
    "note": "爱吃慰藉食物的人最好点什么菜？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'd like to order the chicken pot pie.",
    "note": "我想点鸡肉馅饼。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you make it with a flaky crust?",
    "note": "能做酥皮的嘛？"
  },
  {
    "scene": "diningFood",
    "sentence": "Is the filling made with white meat?",
    "note": "馅料是用鸡胸肉做的嘛？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'll have the shepherd's pie.",
    "note": "我要牧羊人派。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you bring some Worcestershire sauce?",
    "note": "能拿些伍斯特酱吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "What's the best dish for someone who loves street food?",
    "note": "爱吃街头小吃的人最好点什么菜？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'd like to order the tacos al pastor.",
    "note": "我想点牧师塔可。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you make it with pineapple?",
    "note": "能做加菠萝的嘛？"
  },
  {
    "scene": "diningFood",
    "sentence": "Is the meat cooked on a spit?",
    "note": "肉是在烤肉叉上烤的嘛？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'll have the banh mi.",
    "note": "我要越南三明治。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you bring some chili sauce?",
    "note": "能拿些辣椒酱吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "What's the best dish for someone who loves dumplings?",
    "note": "爱吃饺子的人最好点什么菜？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'd like to order the xiao long bao.",
    "note": "我想点小笼包。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you make it with pork and crab?",
    "note": "能做猪肉和蟹肉的嘛？"
  },
  {
    "scene": "diningFood",
    "sentence": "Is the soup inside hot?",
    "note": "里面的汤是热的嘛？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'll have the potstickers.",
    "note": "我要锅贴。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you bring some black vinegar?",
    "note": "能拿些黑醋吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "What's the best dish for someone who loves noodles?",
    "note": "爱吃面条的人最好点什么菜？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'd like to order the ramen.",
    "note": "我想点拉面。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you make it with a rich broth?",
    "note": "能做浓郁汤底的嘛？"
  },
  {
    "scene": "diningFood",
    "sentence": "Is the noodle texture al dente?",
    "note": "面条是弹牙的嘛？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'll have the udon.",
    "note": "我要乌冬面。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you bring some tempura flakes?",
    "note": "能拿些天妇罗脆片吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "What's the best dish for someone who loves rice dishes?",
    "note": "爱吃米饭料理的人最好点什么菜？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'd like to order the bibimbap.",
    "note": "我想点石锅拌饭。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you make it in a hot stone bowl?",
    "note": "能做石锅的嘛？"
  },
  {
    "scene": "diningFood",
    "sentence": "Is the rice crispy at the bottom?",
    "note": "锅巴是脆的嘛？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'll have the jambalaya.",
    "note": "我要什锦饭。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you bring some hot sauce?",
    "note": "能拿些辣酱吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "What's the best dish for someone who loves sandwiches?",
    "note": "爱吃三明治的人最好点什么菜？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'd like to order the club sandwich.",
    "note": "我想点总会三明治。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you make it with turkey?",
    "note": "能做火鸡的嘛？"
  },
  {
    "scene": "diningFood",
    "sentence": "Is the bread toasted?",
    "note": "面包是烤过的嘛？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'll have the croque monsieur.",
    "note": "我要火腿奶酪三明治。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you bring some Dijon mustard?",
    "note": "能拿些第戎芥末酱吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "What's the best dish for someone who loves wraps?",
    "note": "爱吃卷饼的人最好点什么菜？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'd like to order the chicken Caesar wrap.",
    "note": "我想点凯撒鸡肉卷。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you make it with a spinach tortilla?",
    "note": "能做菠菜饼皮的嘛？"
  },
  {
    "scene": "diningFood",
    "sentence": "Is the wrap cut in half?",
    "note": "卷饼是切半的嘛？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'll have the falafel wrap.",
    "note": "我要炸豆丸子卷。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you bring some tahini sauce?",
    "note": "能拿些芝麻酱吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "What's the best dish for someone who loves breakfast all day?",
    "note": "爱吃全天早餐的人最好点什么菜？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'd like to order the huevos rancheros.",
    "note": "我想点墨西哥乡村蛋。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you make it with black beans?",
    "note": "能做黑豆的嘛？"
  },
  {
    "scene": "diningFood",
    "sentence": "Is the salsa spicy?",
    "note": "莎莎酱辣吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'll have the shakshuka.",
    "note": "我要沙克舒卡。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you bring some pita bread?",
    "note": "能拿些皮塔饼吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "What's the best dish for someone who loves tapas?",
    "note": "爱吃西班牙小菜的人最好点什么菜？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'd like to order the patatas bravas.",
    "note": "我想点辣味土豆块。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you make it with aioli?",
    "note": "能做蒜泥蛋黄酱的嘛？"
  },
  {
    "scene": "diningFood",
    "sentence": "Is the paprika smoked?",
    "note": "辣椒粉是熏制的嘛？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'll have the gambas al ajillo.",
    "note": "我要蒜香虾。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you bring some crusty bread?",
    "note": "能拿些硬皮面包吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "What's the best dish for someone who loves fondue?",
    "note": "爱吃火锅的人最好点什么菜？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'd like to order the cheese fondue.",
    "note": "我想点奶酪火锅。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you make it with Emmental and Gruyère?",
    "note": "能做埃曼塔和格鲁耶尔奶酪的嘛？"
  },
  {
    "scene": "diningFood",
    "sentence": "Is the fondue served with bread and vegetables?",
    "note": "火锅配面包和蔬菜吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'll have the chocolate fondue.",
    "note": "我要巧克力火锅。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you bring some marshmallows?",
    "note": "能拿些棉花糖吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "What's the best dish for someone who loves sharing plates?",
    "note": "爱吃分享菜的人最好点什么菜？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'd like to order the mezze platter.",
    "note": "我想点中东开胃菜拼盘。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you make it with hummus and baba ghanoush?",
    "note": "能做鹰嘴豆泥和茄泥的嘛？"
  },
  {
    "scene": "diningFood",
    "sentence": "Is the platter suitable for two people?",
    "note": "拼盘适合两个人吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'll have the sushi platter.",
    "note": "我要寿司拼盘。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you bring some pickled ginger?",
    "note": "能拿些腌姜吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "What's the best dish for someone who loves steak?",
    "note": "爱吃牛排的人最好点什么菜？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'd like to order the filet mignon.",
    "note": "我想点菲力牛排。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you make it with béarnaise sauce?",
    "note": "能做伯纳西酱的嘛？"
  },
  {
    "scene": "diningFood",
    "sentence": "Is the steak tender?",
    "note": "牛排嫩吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'll have the ribeye steak.",
    "note": "我要肋眼牛排。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you bring some compound butter?",
    "note": "能拿些复合黄油吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "What's the best dish for someone who loves seafood towers?",
    "note": "爱吃海鲜塔的人最好点什么菜？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'd like to order the seafood tower.",
    "note": "我想点海鲜塔。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you make it with oysters and shrimp?",
    "note": "能做生蚝和虾的嘛？"
  },
  {
    "scene": "diningFood",
    "sentence": "Is the tower served on ice?",
    "note": "塔是放在冰上的嘛？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'll have the lobster roll.",
    "note": "我要龙虾卷。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you bring some old bay seasoning?",
    "note": "能拿些老湾调味料吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "What's the best dish for someone who loves pasta carbonara?",
    "note": "爱吃卡邦尼意大利面的人最好点什么菜？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'd like to order the carbonara with pancetta.",
    "note": "我想点意式培根卡邦尼。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you make it with fresh eggs?",
    "note": "能做新鲜鸡蛋的嘛？"
  },
  {
    "scene": "diningFood",
    "sentence": "Is the cheese Pecorino Romano?",
    "note": "奶酪是罗马羊奶酪吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'll have the pasta alle vongole.",
    "note": "我要蛤蜊意大利面。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you bring some chili flakes and parsley?",
    "note": "能拿些辣椒片和欧芹吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "What's the best dish for someone who loves risotto?",
    "note": "爱吃烩饭的人最好点什么菜？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'd like to order the truffle risotto.",
    "note": "我想点松露烩饭。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you make it with Arborio rice?",
    "note": "能做阿尔博里奥米的嘛？"
  },
  {
    "scene": "diningFood",
    "sentence": "Is the risotto creamy?",
    "note": "烩饭是奶油状的吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'll have the mushroom risotto with white wine.",
    "note": "我要白酒蘑菇烩饭。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you bring some truffle shavings?",
    "note": "能拿些松露薄片吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "What's the best dish for someone who loves paella?",
    "note": "爱吃海鲜饭的人最好点什么菜？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'd like to order the seafood paella with saffron.",
    "note": "我想点藏红花海鲜饭。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you make it with Bomba rice?",
    "note": "能做邦巴米的嘛？"
  },
  {
    "scene": "diningFood",
    "sentence": "Is the paella cooked in a traditional pan?",
    "note": "海鲜饭是用传统锅煮的嘛？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'll have the mixed paella.",
    "note": "我要混合海鲜饭。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you bring some lemon wedges?",
    "note": "能拿些柠檬角吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "What's the best dish for someone who loves curry?",
    "note": "爱吃咖喱的人最好点什么菜？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'd like to order the green curry with chicken.",
    "note": "我想点绿咖喱鸡。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you make it with Thai basil?",
    "note": "能做泰国罗勒的嘛？"
  },
  {
    "scene": "diningFood",
    "sentence": "Is the curry spicy?",
    "note": "咖喱辣吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'll have the massaman curry.",
    "note": "我要玛莎曼咖喱。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you bring some peanuts and potatoes?",
    "note": "能拿些花生和土豆吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "What's the best dish for someone who loves poke bowls?",
    "note": "爱吃波奇碗的人最好点什么菜？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'd like to order the ahi tuna poke bowl.",
    "note": "我想点金枪鱼波奇碗。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you make it with avocado and edamame?",
    "note": "能做牛油果和毛豆的嘛？"
  },
  {
    "scene": "diningFood",
    "sentence": "Is the fish sushi-grade?",
    "note": "鱼是寿司级的嘛？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'll have the salmon poke bowl.",
    "note": "我要鲑鱼波奇碗。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you bring some sesame seeds?",
    "note": "能拿些芝麻吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "What's the best dish for someone who loves acai bowls?",
    "note": "爱吃巴西莓碗的人最好点什么菜？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'd like to order the acai bowl with granola.",
    "note": "我想点格兰诺拉巴西莓碗。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you make it with coconut flakes?",
    "note": "能做椰子片的嘛？"
  },
  {
    "scene": "diningFood",
    "sentence": "Is the acai pure or mixed?",
    "note": "巴西莓是纯的还是混合的？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'll have the pitaya bowl.",
    "note": "我要火龙果碗。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you bring some chia seeds?",
    "note": "能拿些奇亚籽吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "What's the best dish for someone who loves smoothie bowls?",
    "note": "爱吃思慕雪碗的人最好点什么菜？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'd like to order the green smoothie bowl.",
    "note": "我想点绿色思慕雪碗。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you make it with spinach and banana?",
    "note": "能做菠菜和香蕉的嘛？"
  },
  {
    "scene": "diningFood",
    "sentence": "Is the smoothie bowl thick?",
    "note": "思慕雪碗是稠的吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'll have the berry smoothie bowl.",
    "note": "我要浆果思慕雪碗。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you bring some honey drizzle?",
    "note": "能拿些蜂蜜淋酱吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "What's the best dish for someone who loves charcuterie?",
    "note": "爱吃冷肉拼盘的人最好点什么菜？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'd like to order the charcuterie board with prosciutto.",
    "note": "我想点帕尔玛火腿冷肉拼盘。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you make it with a variety of cured meats?",
    "note": "能做多种腌制肉类的嘛？"
  },
  {
    "scene": "diningFood",
    "sentence": "Is the board served with bread and pickles?",
    "note": "拼盘配面包和腌菜吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'll have the cheese board.",
    "note": "我要奶酪拼盘。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you bring some fig jam?",
    "note": "能拿些无花果果酱吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "What's the best dish for someone who loves dessert?",
    "note": "爱吃甜点的人最好点什么菜？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'd like to order the crème brûlée.",
    "note": "我想点焦糖布丁。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you make it with a caramelized sugar top?",
    "note": "能做焦糖糖衣的嘛？"
  },
  {
    "scene": "diningFood",
    "sentence": "Is the custard creamy?",
    "note": "蛋奶是奶油状的吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'll have the panna cotta.",
    "note": "我要意式奶冻。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you bring some berry sauce?",
    "note": "能拿些浆果酱吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "What's the best dish for someone who loves ice cream?",
    "note": "爱吃冰淇淋的人最好点什么菜？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'd like to order the affogato with vanilla gelato.",
    "note": "我想点香草冰淇淋阿芙佳朵。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you make it with a shot of espresso?",
    "note": "能做加一份浓缩咖啡的嘛？"
  },
  {
    "scene": "diningFood",
    "sentence": "Is the gelato homemade?",
    "note": "冰淇淋是自制的嘛？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'll have the sundae.",
    "note": "我要圣代。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you bring some whipped cream and nuts?",
    "note": "能拿些奶油和坚果吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "What's the best dish for someone who loves crepes?",
    "note": "爱吃可丽饼的人最好点什么菜？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'd like to order the Nutella crepe.",
    "note": "我想点能多益可丽饼。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you make it with bananas?",
    "note": "能做加香蕉的嘛？"
  },
  {
    "scene": "diningFood",
    "sentence": "Is the crepe thin and crispy?",
    "note": "可丽饼是薄脆的嘛？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'll have the savory crepe.",
    "note": "我要咸味可丽饼。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you bring some ham and cheese?",
    "note": "能拿些火腿和奶酪吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "What's the best dish for someone who loves waffles?",
    "note": "爱吃华夫饼的人最好点什么菜？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'd like to order the Belgian waffle.",
    "note": "我想点比利时华夫饼。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you make it with strawberries?",
    "note": "能做加草莓的嘛？"
  },
  {
    "scene": "diningFood",
    "sentence": "Is the waffle crispy on the outside?",
    "note": "华夫饼外面是脆的嘛？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'll have the chicken and waffles.",
    "note": "我要炸鸡华夫饼。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you bring some maple syrup?",
    "note": "能拿些枫糖浆吗？"
  },
  {
    "scene": "diningFood",
    "sentence": "What's the best dish for someone who loves pancakes?",
    "note": "爱吃煎饼的人最好点什么菜？"
  },
  {
    "scene": "diningFood",
    "sentence": "I'd like to order the blueberry pancakes.",
    "note": "我想点蓝莓煎饼。"
  },
  {
    "scene": "diningFood",
    "sentence": "Could you make it with buttermilk?",
    "note": "能做酪乳的嘛？"
  }
];

const phrasesNormalized = phrases.map(p => ({
  ...p,
  note: p.note && p.note.trim() ? p.note : '（中文释义待补充）'
}));

// Build grouped map from normalized data
function buildSceneMap() {
  const map = {};
  phrasesNormalized.forEach(({ scene, sentence, note }) => {
    if (!map[scene]) map[scene] = [];
    map[scene].push([sentence, note]);
  });
  return map;
}

// Hydrate COMMON_ENGLISH_SENTENCES if present, otherwise create it from normalized data.
if (global && typeof global === 'object') {
  if (!global.COMMON_ENGLISH_SENTENCES) {
    global.COMMON_ENGLISH_SENTENCES = buildSceneMap();
  } else {
    phrasesNormalized.forEach(({ scene, sentence, note }) => {
      const list = global.COMMON_ENGLISH_SENTENCES[scene];
      if (!Array.isArray(list)) return;
      const idx = list.findIndex(item => item && item[0] === sentence);
      if (idx !== -1) {
        list[idx][1] = note;
      }
    });
  }
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = phrasesNormalized;
}
if (global) {
  global.phrasesNormalized = phrasesNormalized;
}

})(typeof window !== 'undefined' ? window : (typeof globalThis !== 'undefined' ? globalThis : this));

// 四级词汇数据库
const cet4Words = [
  {
    word: "abandon",
    phonetic: "/əˈbændən/",
    definition: "to leave a place, thing, or person, usually for ever",
    example: "The climbers had to abandon their attempt to reach the summit due to the bad weather."
  },
  {
    word: "ability",
    phonetic: "/əˈbɪləti/",
    definition: "the fact that someone or something is able to do something",
    example: "He has the ability to explain complex ideas clearly."
  },
  {
    word: "abroad",
    phonetic: "/əˈbrɔːd/",
    definition: "in or to a foreign country or countries",
    example: "She's planning to study abroad next year."
  },
  {
    word: "academic",
    phonetic: "/ˌækəˈdemɪk/",
    definition: "relating to education, especially at college or university level",
    example: "His academic achievements have earned him a scholarship."
  },
  {
    word: "accelerate",
    phonetic: "/əkˈseləreɪt/",
    definition: "to happen or make something happen faster or earlier than expected",
    example: "The car accelerated rapidly from 0 to 60 mph."
  },
  {
    word: "accent",
    phonetic: "/ˈæksent/",
    definition: "the way in which people in a particular area, country, or social group pronounce words",
    example: "She speaks English with a French accent."
  },
  {
    word: "acceptable",
    phonetic: "/əkˈseptəbl/",
    definition: "satisfactory and able to be agreed to or approved of",
    example: "Their offer was acceptable to us."
  },
  {
    word: "accommodate",
    phonetic: "/əˈkɒmədeɪt/",
    definition: "to provide someone with a place to stay, live, or work",
    example: "The hotel can accommodate up to 500 guests."
  },
  {
    word: "accomplish",
    phonetic: "/əˈkʌmplɪʃ/",
    definition: "to finish something successfully or to achieve something",
    example: "She has accomplished a great deal in her short career."
  },
  {
    word: "accord",
    phonetic: "/əˈkɔːd/",
    definition: "to give someone or something authority, status, or recognition",
    example: "The government accorded him the rank of colonel."
  },
  {
    word: "account",
    phonetic: "/əˈkaʊnt/",
    definition: "a written or spoken description of an event or situation",
    example: "According to police accounts, the man was arrested at the scene."
  },
  {
    word: "accumulate",
    phonetic: "/əˈkjuːmjəleɪt/",
    definition: "to collect a large number of things over a long period of time",
    example: "Over the years, she has accumulated a vast amount of knowledge about ancient history."
  },
  {
    word: "accuracy",
    phonetic: "/ˈækjərəsi/",
    definition: "the fact of being exact or correct",
    example: "The accuracy of the report has been questioned."
  },
  {
    word: "accurate",
    phonetic: "/ˈækjərət/",
    definition: "correct, exact, and without any mistakes",
    example: "The report was accurate and well-researched."
  },
  {
    word: "accuse",
    phonetic: "/əˈkjuːz/",
    definition: "to say that someone has done something morally wrong, illegal, or unkind",
    example: "He was accused of stealing the money."
  },
  {
    word: "achieve",
    phonetic: "/əˈtʃiːv/",
    definition: "to succeed in reaching a particular goal, status, or standard, especially by making an effort",
    example: "With hard work, she finally achieved her dream of becoming a teacher."
  },
  {
    word: "acquaintance",
    phonetic: "/əˈkweɪntəns/",
    definition: "a person that you know but who is not a close friend",
    example: "He's just an acquaintance, not a friend."
  },
  {
    word: "acquire",
    phonetic: "/əˈkwaɪə/",
    definition: "to get or buy something",
    example: "She has acquired a good knowledge of English."
  },
  {
    word: "adapt",
    phonetic: "/əˈdæpt/",
    definition: "to change something so that it can be used in a different way",
    example: "It takes time for freshmen to adapt to college life."
  },
  {
    word: "adequate",
    phonetic: "/ˈædɪkwət/",
    definition: "enough or good enough for a particular purpose",
    example: "The food was adequate but not excellent."
  },
  {
    word: "adjust",
    phonetic: "/əˈdʒʌst/",
    definition: "to change something slightly to make it more suitable for a particular purpose",
    example: "He adjusted the thermostat to keep the room warm."
  },
  {
    word: "administration",
    phonetic: "/ədˌmɪnɪˈstreɪʃən/",
    definition: "the activities involved in managing or organizing a business or organization",
    example: "The school's administration is responsible for hiring teachers."
  },
  {
    word: "admire",
    phonetic: "/ədˈmaɪə/",
    definition: "to find someone or something attractive and pleasant to look at",
    example: "I admire her for her courage."
  },
  {
    word: "admit",
    phonetic: "/ədˈmɪt/",
    definition: "to agree that something is true, especially unwillingly",
    example: "He finally admitted that he had made a mistake in the project."
  },
  {
    word: "adopt",
    phonetic: "/əˈdɒpt/",
    definition: "to legally take another person's child into your own family and take care of him or her as your own child",
    example: "They adopted a baby girl from China."
  },
  {
    word: "advance",
    phonetic: "/ədˈvɑːns/",
    definition: "to move forward, or to make something move forward",
    example: "The army advanced towards the city."
  },
  {
    word: "advantage",
    phonetic: "/ədˈvɑːntɪdʒ/",
    definition: "a condition giving a greater chance of success",
    example: "His experience gave him an advantage over the other candidates."
  },
  {
    word: "adventure",
    phonetic: "/ədˈventʃə/",
    definition: "an unusual, exciting, and possibly dangerous activity",
    example: "They went on an adventure in the Amazon rainforest."
  },
  {
    word: "advertise",
    phonetic: "/ˈædvətaɪz/",
    definition: "to make something known to the public in a way that encourages people to buy it",
    example: "They're advertising for a new sales manager."
  },
  {
    word: "advice",
    phonetic: "/ədˈvaɪs/",
    definition: "an opinion that someone offers you about what you should do or how you should act in a particular situation",
    example: "She gave me some good advice about how to study for the exam."
  },
  {
    word: "affect",
    phonetic: "/əˈfekt/",
    definition: "to have an influence on someone or something, or to cause a change in someone or something",
    example: "The disease affects millions of people worldwide."
  },
  {
    word: "afford",
    phonetic: "/əˈfɔːd/",
    definition: "to have enough money or time to be able to do something",
    example: "We can't afford to buy a new car right now."
  },
  {
    word: "afraid",
    phonetic: "/əˈfreɪd/",
    definition: "feeling fear or worry",
    example: "I'm afraid of heights."
  },
  {
    word: "afterward",
    phonetic: "/ˈɑːftəwəd/",
    definition: "at a later time; after an event that has already been mentioned",
    example: "We had dinner and went to the movies afterward."
  },
  {
    word: "agency",
    phonetic: "/ˈeɪdʒənsi/",
    definition: "a business that provides a particular service, especially on behalf of other businesses",
    example: "She works for a travel agency."
  },
  {
    word: "agenda",
    phonetic: "/əˈdʒendə/",
    definition: "a list of matters to be discussed at a meeting",
    example: "The main item on the agenda was the budget."
  },
  {
    word: "agent",
    phonetic: "/ˈeɪdʒənt/",
    definition: "a person who acts for or represents another person or organization",
    example: "Our real estate agent found us a great apartment."
  },
  {
    word: "aggressive",
    phonetic: "/əˈɡresɪv/",
    definition: "behaving in an angry and violent way towards another person",
    example: "He became aggressive when he was drunk."
  },
  {
    word: "agriculture",
    phonetic: "/ˈæɡrɪkʌltʃə/",
    definition: "the science or practice of farming",
    example: "Agriculture is the main industry in this region."
  },
  {
    word: "aid",
    phonetic: "/eɪd/",
    definition: "help or support",
    example: "The organization provides aid to people in need."
  },
  {
    word: "aircraft",
    phonetic: "/ˈeəkrɑːft/",
    definition: "any vehicle that can fly",
    example: "The airport handles both commercial and private aircraft."
  },
  {
    word: "alarm",
    phonetic: "/əˈlɑːm/",
    definition: "a device that makes a loud noise to warn people of danger",
    example: "The fire alarm went off in the middle of the night."
  },
  {
    word: "alcohol",
    phonetic: "/ˈælkəhɒl/",
    definition: "a clear liquid that can make you drunk, or any drink that contains this liquid",
    example: "He doesn't drink alcohol."
  },
  {
    word: "alert",
    phonetic: "/əˈlɜːt/",
    definition: "quick to see, understand, and act in a particular situation",
    example: "The dog kept a constant alert watch over the house."
  },
  {
    word: "alien",
    phonetic: "/ˈeɪliən/",
    definition: "a creature from another planet",
    example: "The movie is about aliens visiting Earth."
  },
  {
    word: "alike",
    phonetic: "/əˈlaɪk/",
    definition: "similar to each other",
    example: "The two sisters look very alike."
  },
  {
    word: "alive",
    phonetic: "/əˈlaɪv/",
    definition: "living, not dead",
    example: "The plant is still alive despite the drought."
  },
  {
    word: "alloy",
    phonetic: "/ˈælɔɪ/",
    definition: "a metal that is made by mixing two or more metals together",
    example: "Brass is an alloy of copper and zinc."
  },
  {
    word: "alphabet",
    phonetic: "/ˈælfəbet/",
    definition: "the set of letters used in writing a language",
    example: "Children learn the alphabet before they learn to read."
  },
  {
    word: "alter",
    phonetic: "/ˈɔːltə/",
    definition: "to change something, usually slightly",
    example: "She altered her dress to fit better."
  },
  {
    word: "alternative",
    phonetic: "/ɔːlˈtɜːnətɪv/",
    definition: "a choice between two or more possibilities",
    example: "We need to find an alternative route to avoid the traffic."
  },
  {
    word: "arrange",
    phonetic: "/əˈreɪndʒ/",
    definition: "to plan or prepare for something",
    example: "She helped arrange the meeting between the two managers."
  },
  {
    word: "attend",
    phonetic: "/əˈtend/",
    definition: "to go to an event, place, etc.",
    example: "All students are required to attend the opening ceremony."
  },
  {
    word: "avoid",
    phonetic: "/əˈvɔɪd/",
    definition: "to stay away from someone or something",
    example: "We should avoid eating too much fast food to keep healthy."
  },
  {
    word: "bear",
    phonetic: "/beə/",
    definition: "to accept, tolerate, or endure something",
    example: "She can't bear the noise from the construction site next door."
  },
  {
    word: "belong",
    phonetic: "/bɪˈlɒŋ/",
    definition: "to be owned by someone",
    example: "This book belongs to the school library, so you must return it on time."
  },
  {
    word: "charge",
    phonetic: "/tʃɑːdʒ/",
    definition: "to ask someone to pay money for something",
    example: "The hotel charges 200 yuan per night for a standard room."
  },
  {
    word: "combine",
    phonetic: "/kəmˈbaɪn/",
    definition: "to join together to form a single thing or group",
    example: "We can combine theory with practice to improve our skills."
  },
  {
    word: "consider",
    phonetic: "/kənˈsɪdə/",
    definition: "to think about something carefully",
    example: "He is considering applying for a scholarship to study abroad."
  },
  {
    word: "contain",
    phonetic: "/kənˈteɪn/",
    definition: "to have something inside or as part of itself",
    example: "This bottle contains natural fruit juice without any additives."
  },
  {
    word: "convince",
    phonetic: "/kənˈvɪns/",
    definition: "to make someone believe that something is true",
    example: "She tried to convince her parents to let her study music."
  },
  {
    word: "damage",
    phonetic: "/ˈdæmɪdʒ/",
    definition: "to harm or break something",
    example: "The heavy rain damaged many houses in the small village."
  },
  {
    word: "decline",
    phonetic: "/dɪˈklaɪn/",
    definition: "to decrease in quantity, quality, or importance",
    example: "The number of tourists to this place has declined due to the pandemic."
  },
  {
    word: "deliver",
    phonetic: "/dɪˈlɪvə/",
    definition: "to take goods, letters, etc. to a particular place or person",
    example: "The company promises to deliver the goods within three working days."
  },
  {
    word: "depend",
    phonetic: "/dɪˈpend/",
    definition: "to trust someone or something and know that he, she, or it will help you or do what you want or expect",
    example: "Whether we can go hiking tomorrow depends on the weather."
  },
  {
    word: "deprive",
    phonetic: "/dɪˈpraɪv/",
    definition: "to take something away from someone",
    example: "The war has deprived many children of their homes and education."
  },
  {
    word: "enhance",
    phonetic: "/ɪnˈhɑːns/",
    definition: "to improve the quality, amount, or strength of something",
    example: "Regular exercise can enhance your physical strength and mental health."
  },
  {
    word: "hesitate",
    phonetic: "/ˈhezɪteɪt/",
    definition: "to pause before you do or say something because you are uncertain or nervous",
    example: "She hesitated for a moment before making the important decision."
  },
  {
    word: "indispensable",
    phonetic: "/ˌɪndɪˈspensəbl/",
    definition: "necessary and not able to be replaced",
    example: "Water is indispensable to human life."
  },
  {
    word: "magnitude",
    phonetic: "/ˈmæɡnɪtjuːd/",
    definition: "the great size or importance of something",
    example: "We didn't realize the magnitude of the problem until it was too late."
  },
  {
    word: "pursue",
    phonetic: "/pəˈsjuː/",
    definition: "to try to achieve something",
    example: "She decided to pursue her dream of becoming a famous writer."
  },
  {
    word: "allocate",
    phonetic: "/ˈæləkeɪt/",
    definition: "to give something to a particular person or for a particular purpose",
    example: "The government has allocated a large sum of money to improve the local education system."
  },
  {
    word: "compulsory",
    phonetic: "/kəmˈpʌlsəri/",
    definition: "that must be done because of a law or rule",
    example: "English is a compulsory subject for all students in this school."
  },
  {
    word: "abandon",
    phonetic: "/əˈbændən/",
    definition: "to leave a place, thing, or person, usually for ever",
    example: "The climbers had to abandon their attempt to reach the summit due to the bad weather."
  },
  {
    word: "ability",
    phonetic: "/əˈbɪləti/",
    definition: "the fact that someone or something is able to do something",
    example: "He has the ability to explain complex ideas clearly."
  },
  {
    word: "abroad",
    phonetic: "/əˈbrɔːd/",
    definition: "in or to a foreign country or countries",
    example: "She's planning to study abroad next year."
  },
  {
    word: "academic",
    phonetic: "/ˌækəˈdemɪk/",
    definition: "relating to education, especially at college or university level",
    example: "His academic achievements have earned him a scholarship."
  },
  {
    word: "accelerate",
    phonetic: "/əkˈseləreɪt/",
    definition: "to happen or make something happen faster or earlier than expected",
    example: "The car accelerated rapidly from 0 to 60 mph."
  },
  {
    word: "accent",
    phonetic: "/ˈæksent/",
    definition: "the way in which people in a particular area, country, or social group pronounce words",
    example: "She speaks English with a French accent."
  },
  {
    word: "acceptable",
    phonetic: "/əkˈseptəbl/",
    definition: "satisfactory and able to be agreed to or approved of",
    example: "Their offer was acceptable to us."
  },
  {
    word: "accommodate",
    phonetic: "/əˈkɒmədeɪt/",
    definition: "to provide someone with a place to stay, live, or work",
    example: "The hotel can accommodate up to 500 guests."
  },
  {
    word: "accomplish",
    phonetic: "/əˈkʌmplɪʃ/",
    definition: "to finish something successfully or to achieve something",
    example: "She has accomplished a great deal in her short career."
  },
  {
    word: "accord",
    phonetic: "/əˈkɔːd/",
    definition: "to give someone or something authority, status, or recognition",
    example: "The government accorded him the rank of colonel."
  },
  {
    word: "account",
    phonetic: "/əˈkaʊnt/",
    definition: "a written or spoken description of an event or situation",
    example: "According to police accounts, the man was arrested at the scene."
  },
  {
    word: "accumulate",
    phonetic: "/əˈkjuːmjəleɪt/",
    definition: "to collect a large number of things over a long period of time",
    example: "Over the years, she has accumulated a vast amount of knowledge about ancient history."
  },
  {
    word: "accuracy",
    phonetic: "/ˈækjərəsi/",
    definition: "the fact of being exact or correct",
    example: "The accuracy of the report has been questioned."
  },
  {
    word: "accurate",
    phonetic: "/ˈækjərət/",
    definition: "correct, exact, and without any mistakes",
    example: "The report was accurate and well-researched."
  },
  {
    word: "accuse",
    phonetic: "/əˈkjuːz/",
    definition: "to say that someone has done something morally wrong, illegal, or unkind",
    example: "He was accused of stealing the money."
  },
  {
    word: "achieve",
    phonetic: "/əˈtʃiːv/",
    definition: "to succeed in reaching a particular goal, status, or standard, especially by making an effort",
    example: "With hard work, she finally achieved her dream of becoming a teacher."
  },
  {
    word: "acquaintance",
    phonetic: "/əˈkweɪntəns/",
    definition: "a person that you know but who is not a close friend",
    example: "He's just an acquaintance, not a friend."
  },
  {
    word: "acquire",
    phonetic: "/əˈkwaɪə/",
    definition: "to get or buy something",
    example: "She has acquired a good knowledge of English."
  },
  {
    word: "adapt",
    phonetic: "/əˈdæpt/",
    definition: "to change something so that it can be used in a different way",
    example: "It takes time for freshmen to adapt to college life."
  },
  {
    word: "adequate",
    phonetic: "/ˈædɪkwət/",
    definition: "enough or good enough for a particular purpose",
    example: "The food was adequate but not excellent."
  },
  {
    word: "adjust",
    phonetic: "/əˈdʒʌst/",
    definition: "to change something slightly to make it more suitable for a particular purpose",
    example: "He adjusted the thermostat to keep the room warm."
  },
  {
    word: "administration",
    phonetic: "/ədˌmɪnɪˈstreɪʃən/",
    definition: "the activities involved in managing or organizing a business or organization",
    example: "The school's administration is responsible for hiring teachers."
  },
  {
    word: "admire",
    phonetic: "/ədˈmaɪə/",
    definition: "to find someone or something attractive and pleasant to look at",
    example: "I admire her for her courage."
  },
  {
    word: "admit",
    phonetic: "/ədˈmɪt/",
    definition: "to agree that something is true, especially unwillingly",
    example: "He finally admitted that he had made a mistake in the project."
  },
  {
    word: "adopt",
    phonetic: "/əˈdɒpt/",
    definition: "to legally take another person's child into your own family and take care of him or her as your own child",
    example: "They adopted a baby girl from China."
  },
  {
    word: "advance",
    phonetic: "/ədˈvɑːns/",
    definition: "to move forward, or to make something move forward",
    example: "The army advanced towards the city."
  },
  {
    word: "advantage",
    phonetic: "/ədˈvɑːntɪdʒ/",
    definition: "a condition giving a greater chance of success",
    example: "His experience gave him an advantage over the other candidates."
  },
  {
    word: "adventure",
    phonetic: "/ədˈventʃə/",
    definition: "an unusual, exciting, and possibly dangerous activity",
    example: "They went on an adventure in the Amazon rainforest."
  },
  {
    word: "advertise",
    phonetic: "/ˈædvətaɪz/",
    definition: "to make something known to the public in a way that encourages people to buy it",
    example: "They're advertising for a new sales manager."
  },
  {
    word: "advice",
    phonetic: "/ədˈvaɪs/",
    definition: "an opinion that someone offers you about what you should do or how you should act in a particular situation",
    example: "She gave me some good advice about how to study for the exam."
  },
  {
    word: "affect",
    phonetic: "/əˈfekt/",
    definition: "to have an influence on someone or something, or to cause a change in someone or something",
    example: "The disease affects millions of people worldwide."
  },
  {
    word: "afford",
    phonetic: "/əˈfɔːd/",
    definition: "to have enough money or time to be able to do something",
    example: "We can't afford to buy a new car right now."
  },
  {
    word: "afraid",
    phonetic: "/əˈfreɪd/",
    definition: "feeling fear or worry",
    example: "I'm afraid of heights."
  },
  {
    word: "afterward",
    phonetic: "/ˈɑːftəwəd/",
    definition: "at a later time; after an event that has already been mentioned",
    example: "We had dinner and went to the movies afterward."
  },
  {
    word: "agency",
    phonetic: "/ˈeɪdʒənsi/",
    definition: "a business that provides a particular service, especially on behalf of other businesses",
    example: "She works for a travel agency."
  },
  {
    word: "agenda",
    phonetic: "/əˈdʒendə/",
    definition: "a list of matters to be discussed at a meeting",
    example: "The main item on the agenda was the budget."
  },
  {
    word: "agent",
    phonetic: "/ˈeɪdʒənt/",
    definition: "a person who acts for or represents another person or organization",
    example: "Our real estate agent found us a great apartment."
  },
  {
    word: "aggressive",
    phonetic: "/əˈɡresɪv/",
    definition: "behaving in an angry and violent way towards another person",
    example: "He became aggressive when he was drunk."
  },
  {
    word: "agriculture",
    phonetic: "/ˈæɡrɪkʌltʃə/",
    definition: "the science or practice of farming",
    example: "Agriculture is the main industry in this region."
  },
  {
    word: "aid",
    phonetic: "/eɪd/",
    definition: "help or support",
    example: "The organization provides aid to people in need."
  },
  {
    word: "aircraft",
    phonetic: "/ˈeəkrɑːft/",
    definition: "any vehicle that can fly",
    example: "The airport handles both commercial and private aircraft."
  },
  {
    word: "alarm",
    phonetic: "/əˈlɑːm/",
    definition: "a device that makes a loud noise to warn people of danger",
    example: "The fire alarm went off in the middle of the night."
  },
  {
    word: "alcohol",
    phonetic: "/ˈælkəhɒl/",
    definition: "a clear liquid that can make you drunk, or any drink that contains this liquid",
    example: "He doesn't drink alcohol."
  },
  {
    word: "alert",
    phonetic: "/əˈlɜːt/",
    definition: "quick to see, understand, and act in a particular situation",
    example: "The dog kept a constant alert watch over the house."
  },
  {
    word: "alien",
    phonetic: "/ˈeɪliən/",
    definition: "a creature from another planet",
    example: "The movie is about aliens visiting Earth."
  },
  {
    word: "alike",
    phonetic: "/əˈlaɪk/",
    definition: "similar to each other",
    example: "The two sisters look very alike."
  },
  {
    word: "alive",
    phonetic: "/əˈlaɪv/",
    definition: "living, not dead",
    example: "The plant is still alive despite the drought."
  },
  {
    word: "alloy",
    phonetic: "/ˈælɔɪ/",
    definition: "a metal that is made by mixing two or more metals together",
    example: "Brass is an alloy of copper and zinc."
  },
  {
    word: "alphabet",
    phonetic: "/ˈælfəbet/",
    definition: "the set of letters used in writing a language",
    example: "Children learn the alphabet before they learn to read."
  },
  {
    word: "alter",
    phonetic: "/ˈɔːltə/",
    definition: "to change something, usually slightly",
    example: "She altered her dress to fit better."
  },
  {
    word: "alternative",
    phonetic: "/ɔːlˈtɜːnətɪv/",
    definition: "a choice between two or more possibilities",
    example: "We need to find an alternative route to avoid the traffic."
  },
  {
    word: "allocate",
    phonetic: "/ˈæləkeɪt/",
    definition: "to give something to a particular person or for a particular purpose",
    example: "The government has allocated a large sum of money to improve the local education system."
  },
  {
    word: "aboard",
    phonetic: "/əˈbɔːd/",
    definition: "on or onto a ship, aircraft, bus, or train",
    example: "All passengers must be aboard the ship by 6 PM."
  },
  {
    word: "abstract",
    phonetic: "/ˈæbstrækt/",
    definition: "existing as an idea or quality rather than a physical thing",
    example: "Abstract art is sometimes difficult to understand."
  },
  {
    word: "abundant",
    phonetic: "/əˈbʌndənt/",
    definition: "existing in very large quantities; more than enough",
    example: "The region is abundant in natural resources, such as oil and gas."
  },
  {
    word: "academic",
    phonetic: "/ˌækəˈdemɪk/",
    definition: "relating to education, especially at college or university level",
    example: "His academic achievements have earned him a scholarship."
  },
  {
    word: "accelerate",
    phonetic: "/əkˈseləreɪt/",
    definition: "to happen or make something happen faster or earlier than expected",
    example: "The car accelerated rapidly from 0 to 60 mph."
  },
  {
    word: "accent",
    phonetic: "/ˈæksent/",
    definition: "the way in which people in a particular area, country, or social group pronounce words",
    example: "She speaks English with a French accent."
  },
  {
    word: "acceptable",
    phonetic: "/əkˈseptəbl/",
    definition: "satisfactory and able to be agreed to or approved of",
    example: "Their offer was acceptable to us."
  },
  {
    word: "accommodate",
    phonetic: "/əˈkɒmədeɪt/",
    definition: "to provide someone with a place to stay, live, or work",
    example: "The hotel can accommodate up to 500 guests."
  },
  {
    word: "accomplish",
    phonetic: "/əˈkʌmplɪʃ/",
    definition: "to finish something successfully or to achieve something",
    example: "She has accomplished a great deal in her short career."
  },
  {
    word: "accord",
    phonetic: "/əˈkɔːd/",
    definition: "to give someone or something authority, status, or recognition",
    example: "The government accorded him the rank of colonel."
  },
  {
    word: "account",
    phonetic: "/əˈkaʊnt/",
    definition: "a written or spoken description of an event or situation",
    example: "According to police accounts, the man was arrested at the scene."
  },
  {
    word: "accumulate",
    phonetic: "/əˈkjuːmjəleɪt/",
    definition: "to collect a large number of things over a long period of time",
    example: "Over the years, she has accumulated a vast amount of knowledge about ancient history."
  },
  {
    word: "accuracy",
    phonetic: "/ˈækjərəsi/",
    definition: "the fact of being exact or correct",
    example: "The accuracy of the report has been questioned."
  },
  {
    word: "accurate",
    phonetic: "/ˈækjərət/",
    definition: "correct, exact, and without any mistakes",
    example: "The report was accurate and well-researched."
  },
  {
    word: "accuse",
    phonetic: "/əˈkjuːz/",
    definition: "to say that someone has done something morally wrong, illegal, or unkind",
    example: "He was accused of stealing the money."
  },
  {
    word: "achieve",
    phonetic: "/əˈtʃiːv/",
    definition: "to succeed in reaching a particular goal, status, or standard, especially by making an effort",
    example: "With hard work, she finally achieved her dream of becoming a teacher."
  },
  {
    word: "acquaintance",
    phonetic: "/əˈkweɪntəns/",
    definition: "a person that you know but who is not a close friend",
    example: "He's just an acquaintance, not a friend."
  },
  {
    word: "acquire",
    phonetic: "/əˈkwaɪə/",
    definition: "to get or buy something",
    example: "She has acquired a good knowledge of English."
  },
  {
    word: "adapt",
    phonetic: "/əˈdæpt/",
    definition: "to change something so that it can be used in a different way",
    example: "It takes time for freshmen to adapt to college life."
  },
  {
    word: "adequate",
    phonetic: "/ˈædɪkwət/",
    definition: "enough or good enough for a particular purpose",
    example: "The food was adequate but not excellent."
  },
  {
    word: "adjust",
    phonetic: "/əˈdʒʌst/",
    definition: "to change something slightly to make it more suitable for a particular purpose",
    example: "He adjusted the thermostat to keep the room warm."
  },
  {
    word: "administration",
    phonetic: "/ədˌmɪnɪˈstreɪʃən/",
    definition: "the activities involved in managing or organizing a business or organization",
    example: "The school's administration is responsible for hiring teachers."
  },
  {
    word: "admire",
    phonetic: "/ədˈmaɪə/",
    definition: "to find someone or something attractive and pleasant to look at",
    example: "I admire her for her courage."
  },
  {
    word: "admit",
    phonetic: "/ədˈmɪt/",
    definition: "to agree that something is true, especially unwillingly",
    example: "He finally admitted that he had made a mistake in the project."
  },
  {
    word: "adopt",
    phonetic: "/əˈdɒpt/",
    definition: "to legally take another person's child into your own family and take care of him or her as your own child",
    example: "They adopted a baby girl from China."
  },
  {
    word: "advance",
    phonetic: "/ədˈvɑːns/",
    definition: "to move forward, or to make something move forward",
    example: "The army advanced towards the city."
  },
  {
    word: "advantage",
    phonetic: "/ədˈvɑːntɪdʒ/",
    definition: "a condition giving a greater chance of success",
    example: "His experience gave him an advantage over the other candidates."
  },
  {
    word: "adventure",
    phonetic: "/ədˈventʃə/",
    definition: "an unusual, exciting, and possibly dangerous activity",
    example: "They went on an adventure in the Amazon rainforest."
  },
  {
    word: "advertise",
    phonetic: "/ˈædvətaɪz/",
    definition: "to make something known to the public in a way that encourages people to buy it",
    example: "They're advertising for a new sales manager."
  },
  {
    word: "advice",
    phonetic: "/ədˈvaɪs/",
    definition: "an opinion that someone offers you about what you should do or how you should act in a particular situation",
    example: "She gave me some good advice about how to study for the exam."
  },
  {
    word: "affect",
    phonetic: "/əˈfekt/",
    definition: "to have an influence on someone or something, or to cause a change in someone or something",
    example: "The disease affects millions of people worldwide."
  },
  {
    word: "afford",
    phonetic: "/əˈfɔːd/",
    definition: "to have enough money or time to be able to do something",
    example: "We can't afford to buy a new car right now."
  },
  {
    word: "afraid",
    phonetic: "/əˈfreɪd/",
    definition: "feeling fear or worry",
    example: "I'm afraid of heights."
  },
  {
    word: "afterward",
    phonetic: "/ˈɑːftəwəd/",
    definition: "at a later time; after an event that has already been mentioned",
    example: "We had dinner and went to the movies afterward."
  },
  {
    word: "agency",
    phonetic: "/ˈeɪdʒənsi/",
    definition: "a business that provides a particular service, especially on behalf of other businesses",
    example: "She works for a travel agency."
  },
  {
    word: "agenda",
    phonetic: "/əˈdʒendə/",
    definition: "a list of matters to be discussed at a meeting",
    example: "The main item on the agenda was the budget."
  },
  {
    word: "agent",
    phonetic: "/ˈeɪdʒənt/",
    definition: "a person who acts for or represents another person or organization",
    example: "Our real estate agent found us a great apartment."
  },
  {
    word: "aggressive",
    phonetic: "/əˈɡresɪv/",
    definition: "behaving in an angry and violent way towards another person",
    example: "He became aggressive when he was drunk."
  },
  {
    word: "agriculture",
    phonetic: "/ˈæɡrɪkʌltʃə/",
    definition: "the science or practice of farming",
    example: "Agriculture is the main industry in this region."
  },
  {
    word: "aid",
    phonetic: "/eɪd/",
    definition: "help or support",
    example: "The organization provides aid to people in need."
  },
  {
    word: "aircraft",
    phonetic: "/ˈeəkrɑːft/",
    definition: "any vehicle that can fly",
    example: "The airport handles both commercial and private aircraft."
  },
  {
    word: "alarm",
    phonetic: "/əˈlɑːm/",
    definition: "a device that makes a loud noise to warn people of danger",
    example: "The fire alarm went off in the middle of the night."
  },
  {
    word: "alcohol",
    phonetic: "/ˈælkəhɒl/",
    definition: "a clear liquid that can make you drunk, or any drink that contains this liquid",
    example: "He doesn't drink alcohol."
  },
  {
    word: "alert",
    phonetic: "/əˈlɜːt/",
    definition: "quick to see, understand, and act in a particular situation",
    example: "The dog kept a constant alert watch over the house."
  },
  {
    word: "alien",
    phonetic: "/ˈeɪliən/",
    definition: "a creature from another planet",
    example: "The movie is about aliens visiting Earth."
  },
  {
    word: "alike",
    phonetic: "/əˈlaɪk/",
    definition: "similar to each other",
    example: "The two sisters look very alike."
  },
  {
    word: "alive",
    phonetic: "/əˈlaɪv/",
    definition: "living, not dead",
    example: "The plant is still alive despite the drought."
  },
  {
    word: "alloy",
    phonetic: "/ˈælɔɪ/",
    definition: "a metal that is made by mixing two or more metals together",
    example: "Brass is an alloy of copper and zinc."
  },
  {
    word: "alphabet",
    phonetic: "/ˈælfəbet/",
    definition: "the set of letters used in writing a language",
    example: "Children learn the alphabet before they learn to read."
  },
  {
    word: "alter",
    phonetic: "/ˈɔːltə/",
    definition: "to change something, usually slightly",
    example: "She altered her dress to fit better."
  },
  {
    word: "alternative",
    phonetic: "/ɔːlˈtɜːnətɪv/",
    definition: "a choice between two or more possibilities",
    example: "We need to find an alternative route to avoid the traffic."
  },
  {
    word: "allocate",
    phonetic: "/ˈæləkeɪt/",
    definition: "to give something to a particular person or for a particular purpose",
    example: "The government has allocated a large sum of money to improve the local education system."
  },
  {
    word: "abnormal",
    phonetic: "/æbˈnɔːml/",
    definition: "different from what is usual or average, especially in a way that is bad or worrying",
    example: "The doctor noticed an abnormal growth in the X-ray."
  },
  {
    word: "absolute",
    phonetic: "/ˈæbsəluːt/",
    definition: "total and complete",
    example: "I have absolute confidence in his ability to do the job."
  },
  {
    word: "absolutely",
    phonetic: "/ˈæbsəluːtli/",
    definition: "completely or totally",
    example: "I absolutely love chocolate."
  },
  {
    word: "absorb",
    phonetic: "/əbˈzɔːb/",
    definition: "to take in a liquid, gas, or other substance from the surface or space around",
    example: "The sponge absorbed all the water."
  },
  {
    word: "abstract",
    phonetic: "/ˈæbstrækt/",
    definition: "existing as an idea or quality rather than a physical thing",
    example: "Abstract art is sometimes difficult to understand."
  },
  {
    word: "abundant",
    phonetic: "/əˈbʌndənt/",
    definition: "existing in very large quantities; more than enough",
    example: "The region is abundant in natural resources, such as oil and gas."
  },
  {
    word: "academic",
    phonetic: "/ˌækəˈdemɪk/",
    definition: "relating to education, especially at college or university level",
    example: "His academic achievements have earned him a scholarship."
  },
  {
    word: "accelerate",
    phonetic: "/əkˈseləreɪt/",
    definition: "to happen or make something happen faster or earlier than expected",
    example: "The car accelerated rapidly from 0 to 60 mph."
  },
  {
    word: "accent",
    phonetic: "/ˈæksent/",
    definition: "the way in which people in a particular area, country, or social group pronounce words",
    example: "She speaks English with a French accent."
  },
  {
    word: "acceptable",
    phonetic: "/əkˈseptəbl/",
    definition: "satisfactory and able to be agreed to or approved of",
    example: "Their offer was acceptable to us."
  },
  {
    word: "accommodate",
    phonetic: "/əˈkɒmədeɪt/",
    definition: "to provide someone with a place to stay, live, or work",
    example: "The hotel can accommodate up to 500 guests."
  },
  {
    word: "accomplish",
    phonetic: "/əˈkʌmplɪʃ/",
    definition: "to finish something successfully or to achieve something",
    example: "She has accomplished a great deal in her short career."
  },
  {
    word: "accord",
    phonetic: "/əˈkɔːd/",
    definition: "to give someone or something authority, status, or recognition",
    example: "The government accorded him the rank of colonel."
  },
  {
    word: "account",
    phonetic: "/əˈkaʊnt/",
    definition: "a written or spoken description of an event or situation",
    example: "According to police accounts, the man was arrested at the scene."
  },
  {
    word: "accumulate",
    phonetic: "/əˈkjuːmjəleɪt/",
    definition: "to collect a large number of things over a long period of time",
    example: "Over the years, she has accumulated a vast amount of knowledge about ancient history."
  },
  {
    word: "accuracy",
    phonetic: "/ˈækjərəsi/",
    definition: "the fact of being exact or correct",
    example: "The accuracy of the report has been questioned."
  },
  {
    word: "accurate",
    phonetic: "/ˈækjərət/",
    definition: "correct, exact, and without any mistakes",
    example: "The report was accurate and well-researched."
  },
  {
    word: "accuse",
    phonetic: "/əˈkjuːz/",
    definition: "to say that someone has done something morally wrong, illegal, or unkind",
    example: "He was accused of stealing the money."
  },
  {
    word: "achieve",
    phonetic: "/əˈtʃiːv/",
    definition: "to succeed in reaching a particular goal, status, or standard, especially by making an effort",
    example: "With hard work, she finally achieved her dream of becoming a teacher."
  },
  {
    word: "acquaintance",
    phonetic: "/əˈkweɪntəns/",
    definition: "a person that you know but who is not a close friend",
    example: "He's just an acquaintance, not a friend."
  },
  {
    word: "acquire",
    phonetic: "/əˈkwaɪə/",
    definition: "to get or buy something",
    example: "She has acquired a good knowledge of English."
  },
  {
    word: "adapt",
    phonetic: "/əˈdæpt/",
    definition: "to change something so that it can be used in a different way",
    example: "It takes time for freshmen to adapt to college life."
  },
  {
    word: "adequate",
    phonetic: "/ˈædɪkwət/",
    definition: "enough or good enough for a particular purpose",
    example: "The food was adequate but not excellent."
  },
  {
    word: "adjust",
    phonetic: "/əˈdʒʌst/",
    definition: "to change something slightly to make it more suitable for a particular purpose",
    example: "He adjusted the thermostat to keep the room warm."
  },
  {
    word: "administration",
    phonetic: "/ədˌmɪnɪˈstreɪʃən/",
    definition: "the activities involved in managing or organizing a business or organization",
    example: "The school's administration is responsible for hiring teachers."
  },
  {
    word: "admire",
    phonetic: "/ədˈmaɪə/",
    definition: "to find someone or something attractive and pleasant to look at",
    example: "I admire her for her courage."
  },
  {
    word: "admit",
    phonetic: "/ədˈmɪt/",
    definition: "to agree that something is true, especially unwillingly",
    example: "He finally admitted that he had made a mistake in the project."
  },
  {
    word: "adopt",
    phonetic: "/əˈdɒpt/",
    definition: "to legally take another person's child into your own family and take care of him or her as your own child",
    example: "They adopted a baby girl from China."
  },
  {
    word: "advance",
    phonetic: "/ədˈvɑːns/",
    definition: "to move forward, or to make something move forward",
    example: "The army advanced towards the city."
  },
  {
    word: "advantage",
    phonetic: "/ədˈvɑːntɪdʒ/",
    definition: "a condition giving a greater chance of success",
    example: "His experience gave him an advantage over the other candidates."
  },
  {
    word: "adventure",
    phonetic: "/ədˈventʃə/",
    definition: "an unusual, exciting, and possibly dangerous activity",
    example: "They went on an adventure in the Amazon rainforest."
  },
  {
    word: "advertise",
    phonetic: "/ˈædvətaɪz/",
    definition: "to make something known to the public in a way that encourages people to buy it",
    example: "They're advertising for a new sales manager."
  },
  {
    word: "advice",
    phonetic: "/ədˈvaɪs/",
    definition: "an opinion that someone offers you about what you should do or how you should act in a particular situation",
    example: "She gave me some good advice about how to study for the exam."
  },
  {
    word: "affect",
    phonetic: "/əˈfekt/",
    definition: "to have an influence on someone or something, or to cause a change in someone or something",
    example: "The disease affects millions of people worldwide."
  },
  {
    word: "afford",
    phonetic: "/əˈfɔːd/",
    definition: "to have enough money or time to be able to do something",
    example: "We can't afford to buy a new car right now."
  },
  {
    word: "afraid",
    phonetic: "/əˈfreɪd/",
    definition: "feeling fear or worry",
    example: "I'm afraid of heights."
  },
  {
    word: "afterward",
    phonetic: "/ˈɑːftəwəd/",
    definition: "at a later time; after an event that has already been mentioned",
    example: "We had dinner and went to the movies afterward."
  },
  {
    word: "agency",
    phonetic: "/ˈeɪdʒənsi/",
    definition: "a business that provides a particular service, especially on behalf of other businesses",
    example: "She works for a travel agency."
  },
  {
    word: "agenda",
    phonetic: "/əˈdʒendə/",
    definition: "a list of matters to be discussed at a meeting",
    example: "The main item on the agenda was the budget."
  },
  {
    word: "agent",
    phonetic: "/ˈeɪdʒənt/",
    definition: "a person who acts for or represents another person or organization",
    example: "Our real estate agent found us a great apartment."
  },
  {
    word: "aggressive",
    phonetic: "/əˈɡresɪv/",
    definition: "behaving in an angry and violent way towards another person",
    example: "He became aggressive when he was drunk."
  },
  {
    word: "agriculture",
    phonetic: "/ˈæɡrɪkʌltʃə/",
    definition: "the science or practice of farming",
    example: "Agriculture is the main industry in this region."
  },
  {
    word: "aid",
    phonetic: "/eɪd/",
    definition: "help or support",
    example: "The organization provides aid to people in need."
  },
  {
    word: "aircraft",
    phonetic: "/ˈeəkrɑːft/",
    definition: "any vehicle that can fly",
    example: "The airport handles both commercial and private aircraft."
  },
  {
    word: "alarm",
    phonetic: "/əˈlɑːm/",
    definition: "a device that makes a loud noise to warn people of danger",
    example: "The fire alarm went off in the middle of the night."
  },
  {
    word: "alcohol",
    phonetic: "/ˈælkəhɒl/",
    definition: "a clear liquid that can make you drunk, or any drink that contains this liquid",
    example: "He doesn't drink alcohol."
  },
  {
    word: "alert",
    phonetic: "/əˈlɜːt/",
    definition: "quick to see, understand, and act in a particular situation",
    example: "The dog kept a constant alert watch over the house."
  },
  {
    word: "alien",
    phonetic: "/ˈeɪliən/",
    definition: "a creature from another planet",
    example: "The movie is about aliens visiting Earth."
  },
  {
    word: "alike",
    phonetic: "/əˈlaɪk/",
    definition: "similar to each other",
    example: "The two sisters look very alike."
  },
  {
    word: "alive",
    phonetic: "/əˈlaɪv/",
    definition: "living, not dead",
    example: "The plant is still alive despite the drought."
  },
  {
    word: "alloy",
    phonetic: "/ˈælɔɪ/",
    definition: "a metal that is made by mixing two or more metals together",
    example: "Brass is an alloy of copper and zinc."
  },
  {
    word: "alphabet",
    phonetic: "/ˈælfəbet/",
    definition: "the set of letters used in writing a language",
    example: "Children learn the alphabet before they learn to read."
  },
  {
    word: "alter",
    phonetic: "/ˈɔːltə/",
    definition: "to change something, usually slightly",
    example: "She altered her dress to fit better."
  },
  {
    word: "alternative",
    phonetic: "/ɔːlˈtɜːnətɪv/",
    definition: "a choice between two or more possibilities",
    example: "We need to find an alternative route to avoid the traffic."
  },
  {
    word: "allocate",
    phonetic: "/ˈæləkeɪt/",
    definition: "to give something to a particular person or for a particular purpose",
    example: "The government has allocated a large sum of money to improve the local education system."
  },
    {
    word: "balance",
    phonetic: "/ˈbæləns/",
    definition: "a state where things are of equal weight or force",
    example: "It's important to balance study with relaxation."
  },
  {
    word: "barrier",
    phonetic: "/ˈbæriər/",
    definition: "something that prevents or controls movement",
    example: "Lack of confidence is a major barrier to success."
  },
  {
    word: "beneficial",
    phonetic: "/ˌbenɪˈfɪʃl/",
    definition: "helpful or good",
    example: "Regular exercise is beneficial to both physical and mental health."
  },
  {
    word: "benefit",
    phonetic: "/ˈbenɪfɪt/",
    definition: "an advantage or something that helps",
    example: "Both sides can benefit from the agreement."
  },
  {
    word: "bias",
    phonetic: "/ˈbaɪəs/",
    definition: "a strong feeling in favor of or against one group of people",
    example: "The reporter must avoid any bias in his articles."
  },
  {
    word: "bear",
    phonetic: "/beə/",
    definition: "to accept, tolerate, or endure something",
    example: "She can't bear the noise from the construction site next door."
  },
  {
    word: "belong",
    phonetic: "/bɪˈlɒŋ/",
    definition: "to be owned by someone",
    example: "This book belongs to the school library, so you must return it on time."
  },
  {
    word: "background",
    phonetic: "/ˈbækɡraʊnd/",
    definition: "the history or experience of a person",
    example: "The job requires applicants with a strong technical background."
  },
  {
    word: "bachelor",
    phonetic: "/ˈbætʃələ/",
    definition: "a man who has never been married",
    example: "He's a confirmed bachelor and has no plans to get married."
  },
  {
    word: "badly",
    phonetic: "/ˈbædli/",
    definition: "in a poor or unsatisfactory way",
    example: "The team played badly in the first half but improved after the break."
  },
  {
    word: "baggage",
    phonetic: "/ˈbægɪdʒ/",
    definition: "suitcases, bags, etc. that contain your possessions when you are traveling",
    example: "The airline lost all my baggage during the flight."
  },
  {
    word: "bake",
    phonetic: "/beɪk/",
    definition: "to cook food using dry heat in an oven",
    example: "She baked a delicious cake for the party."
  },
  {
    word: "balance",
    phonetic: "/ˈbæləns/",
    definition: "to keep or put something in a steady position so that it does not fall",
    example: "He balanced the books on his head while walking."
  },
  {
    word: "ban",
    phonetic: "/bæn/",
    definition: "to forbid something officially",
    example: "The government banned smoking in all public places."
  },
  {
    word: "band",
    phonetic: "/bænd/",
    definition: "a group of musicians who play together",
    example: "The band will be performing at the festival next month."
  },
  {
    word: "bankrupt",
    phonetic: "/ˈbæŋkrʌpt/",
    definition: "unable to pay what you owe",
    example: "The company went bankrupt after losing its main contract."
  },
  {
    word: "bare",
    phonetic: "/beə/",
    definition: "not covered by any clothes",
    example: "The tree was bare after the leaves fell in autumn."
  },
  {
    word: "bargain",
    phonetic: "/ˈbɑːɡən/",
    definition: "something you buy that costs less than normal",
    example: "I got this dress at a bargain price during the sale."
  },
  {
    word: "barrel",
    phonetic: "/ˈbærəl/",
    definition: "a large round container, usually made of wood or metal",
    example: "The wine was stored in oak barrels for aging."
  },
  {
    word: "base",
    phonetic: "/beɪs/",
    definition: "the bottom part of something",
    example: "The lamp has a heavy base to keep it stable."
  },
  {
    word: "basic",
    phonetic: "/ˈbeɪsɪk/",
    definition: "simple and not complicated",
    example: "These are the basic rules of the game."
  },
  {
    word: "basically",
    phonetic: "/ˈbeɪsɪkli/",
    definition: "in the most important ways",
    example: "The two theories are basically the same."
  },
  {
    word: "basis",
    phonetic: "/ˈbeɪsɪs/",
    definition: "the most important facts or ideas that support something",
    example: "The report provides a basis for future research."
  },
  {
    word: "battery",
    phonetic: "/ˈbætəri/",
    definition: "a device that produces electricity to provide power",
    example: "The remote control needs new batteries."
  },
  {
    word: "battle",
    phonetic: "/ˈbætl/",
    definition: "a fight between armies, ships, or planes during a war",
    example: "The battle lasted for three days before the city was captured."
  },
  {
    word: "beach",
    phonetic: "/biːtʃ/",
    definition: "an area of sand or small stones at the edge of the sea",
    example: "We spent the day swimming and sunbathing on the beach."
  },
  {
    word: "beam",
    phonetic: "/biːm/",
    definition: "a long piece of wood or metal used to support weight",
    example: "The ceiling is held up by wooden beams."
  },
  {
    word: "bear",
    phonetic: "/beə/",
    definition: "a large, heavy wild animal with thick fur",
    example: "We saw a bear in the forest while hiking."
  },
  {
    word: "beast",
    phonetic: "/biːst/",
    definition: "a large and dangerous animal",
    example: "The beast roared loudly in the jungle."
  },
  {
    word: "beat",
    phonetic: "/biːt/",
    definition: "to hit something many times",
    example: "He beat the drum loudly during the parade."
  },
  {
    word: "beautiful",
    phonetic: "/ˈbjuːtɪfl/",
    definition: "very attractive",
    example: "She wore a beautiful dress to the party."
  },
  {
    word: "beauty",
    phonetic: "/ˈbjuːti/",
    definition: "the quality of being very attractive",
    example: "The beauty of the sunset took our breath away."
  },
  {
    word: "because",
    phonetic: "/bɪˈkɒz/",
    definition: "for the reason that",
    example: "She stayed home because she was feeling sick."
  },
  {
    word: "become",
    phonetic: "/bɪˈkʌm/",
    definition: "to start to be something",
    example: "He became a doctor after studying medicine for seven years."
  },
  {
    word: "beforehand",
    phonetic: "/bɪˈfɔːhænd/",
    definition: "before a particular time or event",
    example: "If you knew the guest list beforehand, why didn't you tell me?"
  },
  {
    word: "behalf",
    phonetic: "/bɪˈhɑːf/",
    definition: "as the representative of someone",
    example: "On behalf of the entire company, I would like to thank you for your hard work."
  },
  {
    word: "behave",
    phonetic: "/bɪˈheɪv/",
    definition: "to act in a particular way",
    example: "The children behaved well during the lesson."
  },
  {
    word: "behavior",
    phonetic: "/bɪˈheɪvjə/",
    definition: "the way that someone behaves",
    example: "His behavior at the party was unacceptable."
  },
  {
    word: "belief",
    phonetic: "/bɪˈliːf/",
    definition: "the feeling of being certain that something exists or is true",
    example: "She has a strong belief in the power of positive thinking."
  },
  {
    word: "believe",
    phonetic: "/bɪˈliːv/",
    definition: "to think that something is true",
    example: "I believe that honesty is the best policy."
  },
  {
    word: "besides",
    phonetic: "/bɪˈsaɪdz/",
    definition: "in addition to",
    example: "Besides studying, she also works part-time."
  },
  {
    word: "bet",
    phonetic: "/bet/",
    definition: "an agreement to risk money on the result of a race, game, etc.",
    example: "He placed a bet on the horse with the best record."
  },
  {
    word: "beyond",
    phonetic: "/bɪˈjɒnd/",
    definition: "on the other side of",
    example: "The mountains beyond the lake are covered with snow."
  },
  {
    word: "bias",
    phonetic: "/ˈbaɪəs/",
    definition: "a preference for one person or group over another",
    example: "The judge was accused of bias in favor of the defendant."
  },
  {
    word: "bizarre",
    phonetic: "/bɪˈzɑːr/",
    definition: "very strange or unusual",
    example: "He wore a bizarre costume to the party."
  },
  {
    word: "blade",
    phonetic: "/bleɪd/",
    definition: "the flat, sharp part of a knife, sword, etc.",
    example: "The blade of the knife was very sharp."
  },
  {
    word: "blame",
    phonetic: "/bleɪm/",
    definition: "to say that someone or something is responsible for something bad",
    example: "She blamed the accident on the bad weather conditions."
  },
  {
    word: "blank",
    phonetic: "/blæŋk/",
    definition: "empty or without any writing, marks, or pictures",
    example: "Please write your name in the blank space at the top of the page."
  },
  {
    word: "blanket",
    phonetic: "/ˈblæŋkɪt/",
    definition: "a large piece of thick cloth used to keep warm",
    example: "She wrapped herself in a warm blanket."
  },
  {
    word: "blast",
    phonetic: "/blɑːst/",
    definition: "a sudden explosion",
    example: "The blast from the bomb could be heard for miles."
  },
  {
    word: "blaze",
    phonetic: "/bleɪz/",
    definition: "a large and very bright fire",
    example: "Firefighters worked for hours to control the blaze."
  },
  {
    word: "bleed",
    phonetic: "/bliːd/",
    definition: "to lose blood",
    example: "He cut his finger and it started to bleed."
  },
  {
    word: "blend",
    phonetic: "/blend/",
    definition: "to mix together",
    example: "She blended the ingredients in a food processor."
  },
  {
    word: "blind",
    phonetic: "/blaɪnd/",
    definition: "unable to see",
    example: "The blind man used a cane to help him walk."
  },
  {
    word: "block",
    phonetic: "/blɒk/",
    definition: "to prevent movement through a space",
    example: "The fallen tree blocked the road."
  },
  {
    word: "blossom",
    phonetic: "/ˈblɒsəm/",
    definition: "a flower, especially on a fruit tree",
    example: "The cherry trees are in blossom."
  },
  {
    word: "blouse",
    phonetic: "/blaʊz/",
    definition: "a shirt worn by women",
    example: "She wore a white blouse with a black skirt."
  },
  {
    word: "blueprint",
    phonetic: "/ˈbluːprɪnt/",
    definition: "a plan or design for something",
    example: "The architect drew up a blueprint for the new building."
  },
  {
    word: "blur",
    phonetic: "/blɜː/",
    definition: "something that is not clear to see",
    example: "The writing on the old document was just a blur."
  },
  {
    word: "blush",
    phonetic: "/blʌʃ/",
    definition: "to become red in the face because of embarrassment",
    example: "She blushed when he complimented her."
  },
  {
    word: "board",
    phonetic: "/bɔːd/",
    definition: "a long, thin, flat piece of wood",
    example: "He nailed the boards together to make a shelf."
  },
  {
    word: "boast",
    phonetic: "/bəʊst/",
    definition: "to talk too proudly about something",
    example: "He's always boasting about his achievements."
  },
  {
    word: "bold",
    phonetic: "/bəʊld/",
    definition: "brave and confident",
    example: "She made a bold decision to quit her job and start her own business."
  },
  {
    word: "bolt",
    phonetic: "/bəʊlt/",
    definition: "a metal object used to fasten things together",
    example: "He tightened the bolts on the machine."
  },
  {
    word: "bomb",
    phonetic: "/bɒm/",
    definition: "an explosive device that is designed to cause damage",
    example: "The bomb exploded in the city center, causing extensive damage."
  },
  {
    word: "bond",
    phonetic: "/bɒnd/",
    definition: "a close connection between people",
    example: "The experience created a strong bond between them."
  },
  {
    word: "bone",
    phonetic: "/bəʊn/",
    definition: "the hard parts inside the body of a person or animal",
    example: "He broke a bone in his leg when he fell."
  },
  {
    word: "bonus",
    phonetic: "/ˈbəʊnəs/",
    definition: "an extra amount of money given as a reward",
    example: "The company gave all employees a Christmas bonus."
  },
  {
    word: "booklet",
    phonetic: "/ˈbʊklət/",
    definition: "a small book with a few pages",
    example: "The tour guide gave us a booklet about the history of the castle."
  },
  {
    word: "boom",
    phonetic: "/buːm/",
    definition: "a loud, deep sound",
    example: "We heard the boom of thunder in the distance."
  },
  {
    word: "boost",
    phonetic: "/buːst/",
    definition: "to increase or improve something",
    example: "The new policy should boost the economy."
  },
  {
    word: "boot",
    phonetic: "/buːt/",
    definition: "a type of shoe that covers the foot and ankle",
    example: "He wore boots to protect his feet from the snow."
  },
  {
    word: "border",
    phonetic: "/ˈbɔːdə/",
    definition: "the line that divides two countries or areas",
    example: "The river forms the border between the two countries."
  },
  {
    word: "bore",
    phonetic: "/bɔː/",
    definition: "to make someone feel tired and not interested",
    example: "The lecture bored me to tears."
  },
  {
    word: "boring",
    phonetic: "/ˈbɔːrɪŋ/",
    definition: "not interesting or exciting",
    example: "The movie was so boring that I fell asleep."
  },
  {
    word: "born",
    phonetic: "/bɔːn/",
    definition: "to come into the world by being born",
    example: "She was born in Paris but grew up in London."
  },
  {
    word: "borrow",
    phonetic: "/ˈbɒrəʊ/",
    definition: "to take something from someone with the intention of giving it back",
    example: "Can I borrow your pen, please?"
  },
  {
    word: "boss",
    phonetic: "/bɒs/",
    definition: "the person who is in charge of a company or department",
    example: "My boss is very demanding but fair."
  },
  {
    word: "both",
    phonetic: "/bəʊθ/",
    definition: "the two things or people mentioned",
    example: "Both of my parents are teachers."
  },
  {
    word: "bother",
    phonetic: "/ˈbɒðə/",
    definition: "to make someone feel slightly worried or upset",
    example: "It bothers me that he never calls when he says he will."
  },
  {
    word: "bottle",
    phonetic: "/ˈbɒtl/",
    definition: "a container made of glass or plastic for holding liquids",
    example: "She drank a bottle of water after her run."
  },
  {
    word: "bottom",
    phonetic: "/ˈbɒtəm/",
    definition: "the lowest part of something",
    example: "The boat sank to the bottom of the lake."
  },
  {
    word: "bounce",
    phonetic: "/baʊns/",
    definition: "to hit a surface and move quickly away from it",
    example: "The ball bounced off the wall and hit him in the face."
  },
  {
    word: "bound",
    phonetic: "/baʊnd/",
    definition: "certain to happen",
    example: "The team is bound to win with their star player back."
  },
  {
    word: "boundary",
    phonetic: "/ˈbaʊndəri/",
    definition: "a line that marks the edge or limit of something",
    example: "The fence marks the boundary between our properties."
  },
  {
    word: "bow",
    phonetic: "/baʊ/",
    definition: "to bend your head or body forward as a sign of respect",
    example: "He bowed to the audience after his performance."
  },
  {
    word: "bowl",
    phonetic: "/bəʊl/",
    definition: "a round container used for holding food or liquid",
    example: "She served soup in a large bowl."
  },
  {
    word: "box",
    phonetic: "/bɒks/",
    definition: "a container with a flat base and sides",
    example: "He put the books in a cardboard box."
  },
  {
    word: "boy",
    phonetic: "/bɔɪ/",
    definition: "a male child or young man",
    example: "The boys were playing football in the park."
  },
  {
    word: "brain",
    phonetic: "/breɪn/",
    definition: "the organ inside the head that controls thought, memory, etc.",
    example: "Scientists are studying how the brain works."
  },
  {
    word: "brake",
    phonetic: "/breɪk/",
    definition: "a device used to make a vehicle go slower or stop",
    example: "He slammed on the brakes to avoid hitting the dog."
  },
  {
    word: "branch",
    phonetic: "/brɑːntʃ/",
    definition: "a part of a tree that grows out from the trunk",
    example: "The monkey was sitting on a branch."
  },
  {
    word: "brand",
    phonetic: "/brænd/",
    definition: "a type of product made by a particular company",
    example: "What brand of toothpaste do you use?"
  },
  {
    word: "brass",
    phonetic: "/brɑːs/",
    definition: "a yellow metal made from copper and zinc",
    example: "The doorknob was made of brass."
  },
  {
    word: "brave",
    phonetic: "/breɪv/",
    definition: "showing courage",
    example: "She was brave enough to confront the burglar."
  },
  {
    word: "breach",
    phonetic: "/briːtʃ/",
    definition: "an act of breaking a law, promise, or agreement",
    example: "This was a clear breach of the international agreement."
  },
  {
    word: "bread",
    phonetic: "/bred/",
    definition: "a food made from flour, water, and yeast",
    example: "She baked a fresh loaf of bread this morning."
  },
  {
    word: "break",
    phonetic: "/breɪk/",
    definition: "to separate into pieces as a result of force",
    example: "He broke the vase when he knocked it off the table."
  },
  {
    word: "breakfast",
    phonetic: "/ˈbrekfəst/",
    definition: "the first meal of the day",
    example: "We had eggs and toast for breakfast."
  },
  {
    word: "breast",
    phonetic: "/brest/",
    definition: "either of the two soft, rounded parts on a woman's chest",
    example: "She noticed a lump in her breast during a self-examination."
  },
  {
    word: "breath",
    phonetic: "/breθ/",
    definition: "the air that you take into and out of your lungs",
    example: "She took a deep breath before diving into the pool."
  },
  {
    word: "breathe",
    phonetic: "/briːð/",
    definition: "to take air into your lungs and send it out again",
    example: "It's difficult to breathe at high altitudes."
  },
  {
    word: "breed",
    phonetic: "/briːd/",
    definition: "to keep animals for the purpose of producing young animals",
    example: "The farmer breeds cattle for meat."
  },
  {
    word: "breeze",
    phonetic: "/briːz/",
    definition: "a light wind",
    example: "A gentle breeze was blowing through the trees."
  },
  {
    word: "brick",
    phonetic: "/brɪk/",
    definition: "a rectangular block of baked clay used for building",
    example: "The house was built with red bricks."
  },
  {
    word: "bride",
    phonetic: "/braɪd/",
    definition: "a woman who is getting married or has just got married",
    example: "The bride looked beautiful in her white dress."
  },
  {
    word: "bridge",
    phonetic: "/brɪdʒ/",
    definition: "a structure built over a river, road, etc. so that people can cross",
    example: "The new bridge will reduce traffic congestion in the city."
  },
  {
    word: "brief",
    phonetic: "/briːf/",
    definition: "lasting only a short time",
    example: "We had a brief conversation before the meeting started."
  },
  {
    word: "bright",
    phonetic: "/braɪt/",
    definition: "full of light",
    example: "The sun was bright and hot."
  },
  {
    word: "brilliant",
    phonetic: "/ˈbrɪliənt/",
    definition: "extremely clever or impressive",
    example: "She came up with a brilliant solution to the problem."
  },
  {
    word: "brim",
    phonetic: "/brɪm/",
    definition: "the edge of a cup, bowl, etc.",
    example: "The glass was filled to the brim with water."
  },
  {
    word: "bring",
    phonetic: "/brɪŋ/",
    definition: "to take something or someone to a place",
    example: "Could you bring me a glass of water, please?"
  },
  {
    word: "brisk",
    phonetic: "/brɪsk/",
    definition: "quick and energetic",
    example: "We took a brisk walk in the park to warm up."
  },
  {
    word: "brochure",
    phonetic: "/ˈbrəʊʃə/",
    definition: "a small book containing information about a product or service",
    example: "The travel agency gave us a brochure about holiday destinations."
  },
  {
    word: "bronze",
    phonetic: "/brɒnz/",
    definition: "a yellowish-brown metal made from copper and tin",
    example: "The statue was made of bronze."
  },
  {
    word: "brood",
    phonetic: "/bruːd/",
    definition: "to think a lot about something that makes you sad or worried",
    example: "She brooded over her failure for weeks."
  },
  {
    word: "brook",
    phonetic: "/brʊk/",
    definition: "a small stream",
    example: "The children played in the brook during the summer."
  },
  {
    word: "broom",
    phonetic: "/bruːm/",
    definition: "a brush with a long handle used for sweeping",
    example: "She swept the floor with a broom."
  },
  {
    word: "brother",
    phonetic: "/ˈbrʌðə/",
    definition: "a male who has the same parents as you",
    example: "My brother is two years older than me."
  },
  {
    word: "brow",
    phonetic: "/braʊ/",
    definition: "the part of the face above the eyes",
    example: "He furrowed his brow in concentration."
  },
  {
    word: "brown",
    phonetic: "/braʊn/",
    definition: "the color of earth or coffee",
    example: "She has brown hair and blue eyes."
  },
  {
    word: "bubble",
    phonetic: "/ˈbʌbl/",
    definition: "a ball of air or gas in a liquid",
    example: "The water in the pot began to bubble as it boiled."
  },
  {
    word: "bucket",
    phonetic: "/ˈbʌkɪt/",
    definition: "a container with a handle used for carrying liquids",
    example: "He filled the bucket with water from the well."
  },
  {
    word: "bud",
    phonetic: "/bʌd/",
    definition: "a small part of a plant that develops into a flower or leaf",
    example: "The rosebuds will open into flowers in a few days."
  },
  {
    word: "budget",
    phonetic: "/ˈbʌdʒɪt/",
    definition: "a plan for how to spend money",
    example: "We need to budget for unexpected expenses."
  },
  {
    word: "buffalo",
    phonetic: "/ˈbʌfələʊ/",
    definition: "a large animal like a cow with horns that curve upwards",
    example: "Buffalo once roamed the Great Plains in large numbers."
  },
  {
    word: "buffer",
    phonetic: "/ˈbʌfə/",
    definition: "something that protects against harm or damage",
    example: "The trees act as a buffer against strong winds."
  },
  {
    word: "bug",
    phonetic: "/bʌɡ/",
    definition: "a small insect",
    example: "There are lots of bugs in the garden during the summer."
  },
  {
    word: "build",
    phonetic: "/bɪld/",
    definition: "to make something by putting parts together",
    example: "They built a new house in the suburbs."
  },
  {
    word: "building",
    phonetic: "/ˈbɪldɪŋ/",
    definition: "a structure with walls and a roof",
    example: "The tallest building in the city is the new skyscraper."
  },
  {
    word: "bulb",
    phonetic: "/bʌlb/",
    definition: "the glass part of an electric lamp that produces light",
    example: "The light bulb needs to be replaced."
  },
  {
    word: "bulge",
    phonetic: "/bʌldʒ/",
    definition: "a rounded part that sticks out from a surface",
    example: "There was a bulge in the carpet where the floor was uneven."
  },
  {
    word: "bulk",
    phonetic: "/bʌlk/",
    definition: "the size or mass of something large",
    example: "The bulk of the work has already been done."
  },
  {
    word: "bull",
    phonetic: "/bʊl/",
    definition: "a male cow",
    example: "The farmer keeps a bull for breeding."
  },
  {
    word: "bullet",
    phonetic: "/ˈbʊlɪt/",
    definition: "a small metal object fired from a gun",
    example: "The bullet hit the target in the center."
  },
  {
    word: "bulletin",
    phonetic: "/ˈbʊlətɪn/",
    definition: "a short news report",
    example: "The school issued a bulletin about the upcoming exams."
  },
  {
    word: "bully",
    phonetic: "/ˈbʊli/",
    definition: "a person who frightens or hurts people who are weaker",
    example: "The teacher dealt with the bully who was picking on younger students."
  },
  {
    word: "bump",
    phonetic: "/bʌmp/",
    definition: "to hit something with force",
    example: "I bumped my head on the low ceiling."
  },
  {
    word: "bunch",
    phonetic: "/bʌntʃ/",
    definition: "a group of things that are fastened or growing together",
    example: "She picked a bunch of flowers from the garden."
  },
  {
    word: "bundle",
    phonetic: "/ˈbʌndl/",
    definition: "a number of things tied or wrapped together",
    example: "He carried a bundle of sticks on his back."
  },
  {
    word: "burden",
    phonetic: "/ˈbɜːdn/",
    definition: "a heavy load that is difficult to carry",
    example: "He didn't want to be a burden to his family."
  },
  {
    word: "bureau",
    phonetic: "/ˈbjʊərəʊ/",
    definition: "a government department or an office",
    example: "The weather bureau issued a warning about the storm."
  },
  {
    word: "bureaucracy",
    phonetic: "/bjʊəˈrɒkrəsi/",
    definition: "the system of rules and officials in a government or organization",
    example: "We had to deal with a lot of bureaucracy to get the permit."
  },
  {
    word: "burglar",
    phonetic: "/ˈbɜːɡlə/",
    definition: "a person who enters a building illegally to steal things",
    example: "The burglar broke into the house through a window."
  },
  {
    word: "burn",
    phonetic: "/bɜːn/",
    definition: "to be on fire or to make something be on fire",
    example: "The fire burned brightly in the fireplace."
  },
  {
    word: "burst",
    phonetic: "/bɜːst/",
    definition: "to break open or apart suddenly",
    example: "The balloon burst with a loud pop."
  },
  {
    word: "bury",
    phonetic: "/ˈberi/",
    definition: "to put a dead body into the ground",
    example: "They buried their dog in the backyard."
  },
  {
    word: "bus",
    phonetic: "/bʌs/",
    definition: "a large vehicle that carries passengers",
    example: "She takes the bus to work every day."
  },
  {
    word: "bush",
    phonetic: "/bʊʃ/",
    definition: "a large plant with many branches growing close together",
    example: "The rabbit hid behind the bush."
  },
  {
    word: "business",
    phonetic: "/ˈbɪznəs/",
    definition: "the activity of making, buying, or selling goods or services",
    example: "He started his own business after graduating from college."
  },
  {
    word: "busy",
    phonetic: "/ˈbɪzi/",
    definition: "having a lot of things to do",
    example: "She's very busy with her new job."
  },
  {
    word: "but",
    phonetic: "/bʌt/",
    definition: "used to introduce something that is different or opposite",
    example: "I wanted to go, but I was too tired."
  },
  {
    word: "butcher",
    phonetic: "/ˈbʊtʃə/",
    definition: "a person who sells meat",
    example: "The butcher recommended the beef for the stew."
  },
  {
    word: "butter",
    phonetic: "/ˈbʌtə/",
    definition: "a yellow substance made from cream that you spread on bread",
    example: "She put butter on her toast."
  },
  {
    word: "butterfly",
    phonetic: "/ˈbʌtəflaɪ/",
    definition: "an insect with large, colorful wings",
    example: "Butterflies were fluttering around the flowers."
  },
  {
    word: "button",
    phonetic: "/ˈbʌtn/",
    definition: "a small round object used to fasten clothes",
    example: "She sewed a button back onto her shirt."
  },
  {
    word: "bypass",
    phonetic: "/ˈbaɪpɑːs/",
    definition: "a road that goes around a town or city to avoid traffic",
    example: "We took the bypass to avoid the city center."
  },
  {
    word: "byproduct",
    phonetic: "/ˈbaɪprɒdʌkt/",
    definition: "something that is produced as a result of making something else",
    example: "Methane is a byproduct of the digestion process in cows."
  },
  {
    word: "byway",
    phonetic: "/ˈbaɪweɪ/",
    definition: "a small road that is not used much",
    example: "They discovered a beautiful cottage down a quiet byway."
  },
  {
    word: "bygone",
    phonetic: "/ˈbaɪɡɒn/",
    definition: "belonging to a time in the past",
    example: "The museum displays artifacts from bygone eras."
  },
  {
    word: "bylaw",
    phonetic: "/ˈbaɪlɔː/",
    definition: "a rule made by a local authority or organization",
    example: "According to the club's bylaws, members must pay their dues by the end of the month."
  },
  {
    word: "bypass",
    phonetic: "/ˈbaɪpɑːs/",
    definition: "to avoid a place or thing",
    example: "The new highway bypasses the small town."
  },
  {
    word: "byproduct",
    phonetic: "/ˈbaɪprɒdʌkt/",
    definition: "something produced in addition to the main product",
    example: "Glycerin is a byproduct of soap making."
  },
  {
    word: "byword",
    phonetic: "/ˈbaɪwɜːd/",
    definition: "a word or phrase that is often used to describe a person or thing",
    example: "He became a byword for honesty in the community."
  },
    {
    word: "campaign",
    phonetic: "/kæmˈpeɪn/",
    definition: "a series of planned activities to achieve a goal",
    example: "The government has launched a campaign against smoking."
  },
  {
    word: "candidate",
    phonetic: "/ˈkændɪdət/",
    definition: "a person who applies for a job or is nominated for an election",
    example: "There are three candidates for the position."
  },
  {
    word: "category",
    phonetic: "/ˈkætəɡɔːri/",
    definition: "a group of people or things that have similar characteristics",
    example: "The books are divided into two main categories: fiction and non-fiction."
  },
  {
    word: "cease",
    phonetic: "/siːs/",
    definition: "to stop happening or existing",
    example: "The factory will cease operations next month."
  },
  {
    word: "challenge",
    phonetic: "/ˈtʃælɪndʒ/",
    definition: "a difficult task or situation that tests someone's abilities",
    example: "This new job will be a great challenge for him."
  },
  {
    word: "channel",
    phonetic: "/ˈtʃænl/",
    definition: "a television or radio station; a way of communicating",
    example: "We need to channel more resources into education."
  },
  {
    word: "characteristic",
    phonetic: "/ˌkærəktəˈrɪstɪk/",
    definition: "a feature or quality that is typical of someone or something",
    example: "Sympathy is a characteristic of human beings."
  },
  {
    word: "circumstance",
    phonetic: "/ˈsɜːrkəmstæns/",
    definition: "the conditions or facts that affect a situation",
    example: "Under no circumstances should you give out your password."
  },
  {
    word: "claim",
    phonetic: "/kleɪm/",
    definition: "to say that something is true, even though it has not been proved",
    example: "He claims to have seen the famous actor."
  },
  {
    word: "commit",
    phonetic: "/kəˈmɪt/",
    definition: "to do something illegal or wrong",
    example: "The government has committed substantial funds to healthcare."
  },
  {
    word: "charge",
    phonetic: "/tʃɑːdʒ/",
    definition: "to ask someone to pay money for something",
    example: "The hotel charges 200 yuan per night for a standard room."
  },
  {
    word: "combine",
    phonetic: "/kəmˈbaɪn/",
    definition: "to join together to form a single thing or group",
    example: "We can combine theory with practice to improve our skills."
  },
  {
    word: "consider",
    phonetic: "/kənˈsɪdə/",
    definition: "to think about something carefully",
    example: "He is considering applying for a scholarship to study abroad."
  },
  {
    word: "contain",
    phonetic: "/kənˈteɪn/",
    definition: "to have something inside or as part of itself",
    example: "This bottle contains natural fruit juice without any additives."
  },
  {
    word: "convince",
    phonetic: "/kənˈvɪns/",
    definition: "to make someone believe that something is true",
    example: "She tried to convince her parents to let her study music."
  },
  {
    word: "compulsory",
    phonetic: "/kəmˈpʌlsəri/",
    definition: "that must be done because of a law or rule",
    example: "English is a compulsory subject for all students in this school."
  },
  {
    word: "cabbage",
    phonetic: "/ˈkæbɪdʒ/",
    definition: "a round vegetable with green leaves that is eaten cooked or raw",
    example: "She made a salad with cabbage and carrots."
  },
  {
    word: "cabin",
    phonetic: "/ˈkæbɪn/",
    definition: "a small wooden house in the country or mountains",
    example: "We spent the weekend in a cabin by the lake."
  },
  {
    word: "cabinet",
    phonetic: "/ˈkæbɪnɪt/",
    definition: "a piece of furniture with doors and shelves for storing things",
    example: "The medicine is in the cabinet above the sink."
  },
  {
    word: "cable",
    phonetic: "/ˈkeɪbl/",
    definition: "a set of wires covered in plastic or rubber that carries electricity or electronic signals",
    example: "The cable connecting the computer to the printer is broken."
  },
  {
    word: "cafe",
    phonetic: "/ˈkæfeɪ/",
    definition: "a small restaurant where you can buy drinks and simple meals",
    example: "Let's meet at the cafe on the corner."
  },
  {
    word: "cage",
    phonetic: "/keɪdʒ/",
    definition: "a structure made of metal bars or wire that is used to keep animals or birds in",
    example: "The birds were singing in their cage."
  },
  {
    word: "cake",
    phonetic: "/keɪk/",
    definition: "a sweet food made from flour, eggs, sugar, and butter, baked in an oven",
    example: "She baked a chocolate cake for his birthday."
  },
  {
    word: "calculate",
    phonetic: "/ˈkælkjuleɪt/",
    definition: "to find out how much something will cost, how long something will take, etc., using numbers",
    example: "I need to calculate how much money I'll need for the trip."
  },
  {
    word: "calculator",
    phonetic: "/ˈkælkjuleɪtə/",
    definition: "a small electronic device used for doing mathematical calculations",
    example: "You can use a calculator to check your answers."
  },
  {
    word: "calendar",
    phonetic: "/ˈkælɪndə/",
    definition: "a system for measuring time in days, weeks, months, and years",
    example: "According to the calendar, the meeting is on Friday."
  },
  {
    word: "call",
    phonetic: "/kɔːl/",
    definition: "to telephone someone",
    example: "I'll call you when I arrive at the airport."
  },
  {
    word: "calm",
    phonetic: "/kɑːm/",
    definition: "peaceful and quiet, with no excitement or worry",
    example: "The sea was calm and the sky was clear."
  },
  {
    word: "camel",
    phonetic: "/ˈkæml/",
    definition: "a large animal with a long neck that lives in deserts and can go for a long time without water",
    example: "Camels are often used for transportation in desert areas."
  },
  {
    word: "camera",
    phonetic: "/ˈkæmərə/",
    definition: "a device used for taking photographs or making films",
    example: "Don't forget to bring your camera to the party."
  },
  {
    word: "camp",
    phonetic: "/kæmp/",
    definition: "a place where people live in tents or temporary buildings, especially for a holiday or while working",
    example: "We're going to set up camp by the lake."
  },
  {
    word: "campaign",
    phonetic: "/kæmˈpeɪn/",
    definition: "a series of planned activities to achieve a goal, especially in politics or business",
    example: "The company launched a new advertising campaign."
  },
  {
    word: "can",
    phonetic: "/kæn/",
    definition: "to be able to do something",
    example: "I can speak English and a little French."
  },
  {
    word: "canal",
    phonetic: "/kəˈnæl/",
    definition: "a long, narrow stretch of water that has been made for boats to travel along or to carry water",
    example: "The Panama Canal connects the Atlantic and Pacific Oceans."
  },
  {
    word: "cancel",
    phonetic: "/ˈkænsəl/",
    definition: "to decide that something that was planned will not happen",
    example: "They had to cancel the picnic because of the rain."
  },
  {
    word: "cancer",
    phonetic: "/ˈkænsə/",
    definition: "a serious disease in which cells in a part of the body grow in a way that is not normal",
    example: "Early detection of cancer can save lives."
  },
  {
    word: "candidate",
    phonetic: "/ˈkændɪdət/",
    definition: "a person who is trying to be elected or who is applying for a job",
    example: "There are three candidates running for president."
  },
  {
    word: "candle",
    phonetic: "/ˈkændl/",
    definition: "a stick of wax with a wick in the middle that produces light when it burns",
    example: "We lit candles to create a romantic atmosphere."
  },
  {
    word: "candy",
    phonetic: "/ˈkændi/",
    definition: "sweet food made from sugar or chocolate",
    example: "The children received candy as a treat."
  },
  {
    word: "cannon",
    phonetic: "/ˈkænən/",
    definition: "a large gun that fires heavy metal balls or shells",
    example: "The castle was defended by cannons."
  },
  {
    word: "canoe",
    phonetic: "/kəˈnuː/",
    definition: "a long, narrow boat that is moved through the water using a paddle",
    example: "We went canoeing on the river."
  },
  {
    word: "canteen",
    phonetic: "/kænˈtiːn/",
    definition: "a place where food and drink are sold in a factory, school, etc.",
    example: "The staff canteen serves hot meals every day."
  },
  {
    word: "cap",
    phonetic: "/kæp/",
    definition: "a soft flat hat with a peak that is worn by men and boys",
    example: "He always wears a baseball cap backwards."
  },
  {
    word: "capable",
    phonetic: "/ˈkeɪpəbl/",
    definition: "having the ability or skill to do something",
    example: "She is capable of handling the job on her own."
  },
  {
    word: "capacity",
    phonetic: "/kəˈpæsəti/",
    definition: "the amount that something can hold or produce",
    example: "The stadium has a seating capacity of 50,000."
  },
  {
    word: "capital",
    phonetic: "/ˈkæpɪtl/",
    definition: "the most important city or town of a country or region",
    example: "Beijing is the capital of China."
  },
  {
    word: "captain",
    phonetic: "/ˈkæptɪn/",
    definition: "the person who is in charge of a ship, aircraft, or sports team",
    example: "The captain of the ship gave the order to abandon ship."
  },
  {
    word: "capture",
    phonetic: "/ˈkæptʃə/",
    definition: "to take someone as a prisoner, or to take something by force",
    example: "The soldiers captured the enemy's headquarters."
  },
  {
    word: "car",
    phonetic: "/kɑː/",
    definition: "a road vehicle with an engine, four wheels, and seats for a small number of people",
    example: "I need to buy a new car."
  },
  {
    word: "carbon",
    phonetic: "/ˈkɑːbən/",
    definition: "a chemical element that is found in all plants and animals",
    example: "Carbon dioxide is a greenhouse gas."
  },
  {
    word: "card",
    phonetic: "/kɑːd/",
    definition: "a small piece of stiff paper or plastic used for various purposes",
    example: "She gave me her business card."
  },
  {
    word: "cardboard",
    phonetic: "/ˈkɑːdbɔːd/",
    definition: "thick, stiff paper that is used for making boxes, etc.",
    example: "The children made a castle out of cardboard boxes."
  },
  {
    word: "career",
    phonetic: "/kəˈrɪə/",
    definition: "the job or profession that someone does for a long period of their life",
    example: "She's had a successful career in medicine."
  },
  {
    word: "careful",
    phonetic: "/ˈkeəfl/",
    definition: "taking care to avoid mistakes or accidents",
    example: "Be careful when you cross the road."
  },
  {
    word: "caress",
    phonetic: "/kəˈres/",
    definition: "to touch someone or something gently and lovingly",
    example: "She caressed her baby's cheek."
  },
  {
    word: "cargo",
    phonetic: "/ˈkɑːɡəʊ/",
    definition: "goods that are carried by ship, aircraft, or vehicle",
    example: "The ship was carrying a cargo of oil."
  },
  {
    word: "carpenter",
    phonetic: "/ˈkɑːpəntə/",
    definition: "a person whose job is making and repairing wooden objects and structures",
    example: "The carpenter built a new bookshelf for the library."
  },
  {
    word: "carpet",
    phonetic: "/ˈkɑːpɪt/",
    definition: "a thick covering for a floor, usually made of wool or synthetic fibers",
    example: "The carpet in the living room needs to be cleaned."
  },
  {
    word: "carriage",
    phonetic: "/ˈkærɪdʒ/",
    definition: "a vehicle with wheels that is pulled by horses",
    example: "The royal family arrived in a horse-drawn carriage."
  },
  {
    word: "carrier",
    phonetic: "/ˈkæriə/",
    definition: "a person or thing that carries something",
    example: "Mosquitoes are carriers of malaria."
  },
  {
    word: "carrot",
    phonetic: "/ˈkærət/",
    definition: "a long, thin orange vegetable that grows under the ground",
    example: "Rabbits like to eat carrots."
  },
  {
    word: "carry",
    phonetic: "/ˈkæri/",
    definition: "to hold something or someone while moving from one place to another",
    example: "Could you help me carry these boxes?"
  },
  {
    word: "cart",
    phonetic: "/kɑːt/",
    definition: "a vehicle with wheels that is pulled by an animal or person",
    example: "The farmer loaded the cart with hay."
  },
  {
    word: "cartoon",
    phonetic: "/kɑːˈtuːn/",
    definition: "a drawing or series of drawings that tell a story or make people laugh",
    example: "Children enjoy watching cartoons on television."
  },
  {
    word: "carve",
    phonetic: "/kɑːv/",
    definition: "to cut shapes or patterns into wood or stone",
    example: "He carved his name into the tree trunk."
  },
  {
    word: "case",
    phonetic: "/keɪs/",
    definition: "a container for holding or protecting something",
    example: "She put her glasses in their case."
  },
  {
    word: "cash",
    phonetic: "/kæʃ/",
    definition: "money in the form of notes and coins",
    example: "Do you have enough cash to pay for dinner?"
  },
  {
    word: "cassette",
    phonetic: "/kəˈset/",
    definition: "a small plastic case containing magnetic tape for recording sound or video",
    example: "I still have some old music cassettes."
  },
  {
    word: "cast",
    phonetic: "/kɑːst/",
    definition: "to throw something with force",
    example: "He cast the fishing line into the water."
  },
  {
    word: "castle",
    phonetic: "/ˈkɑːsl/",
    definition: "a large building with thick walls and towers that was built in the past to protect people",
    example: "The castle was built in the 12th century."
  },
  {
    word: "casual",
    phonetic: "/ˈkæʒuəl/",
    definition: "relaxed and not formal",
    example: "We're having a casual dinner, so you don't need to dress up."
  },
  {
    word: "cat",
    phonetic: "/kæt/",
    definition: "a small animal with fur, four legs, and a tail that is kept as a pet",
    example: "Our cat likes to sleep on the windowsill."
  },
  {
    word: "catalog",
    phonetic: "/ˈkætəlɒɡ/",
    definition: "a list of items, especially one in a book or on a computer",
    example: "The library has a catalog of all its books."
  },
  {
    word: "catch",
    phonetic: "/kætʃ/",
    definition: "to take hold of something that is moving through the air",
    example: "He caught the ball with one hand."
  },
  {
    word: "category",
    phonetic: "/ˈkætəɡɔːri/",
    definition: "a group of people or things that have similar characteristics",
    example: "Books are divided into different categories in the library."
  },
  {
    word: "cater",
    phonetic: "/ˈkeɪtə/",
    definition: "to provide food and drinks for an event or group of people",
    example: "The restaurant caters for weddings and parties."
  },
  {
    word: "cathedral",
    phonetic: "/kəˈθiːdrəl/",
    definition: "a very large and important church",
    example: "The cathedral in Milan is famous for its Gothic architecture."
  },
  {
    word: "cattle",
    phonetic: "/ˈkætl/",
    definition: "cows and bulls that are kept for their milk or meat",
    example: "The farmer has a herd of cattle."
  },
  {
    word: "cause",
    phonetic: "/kɔːz/",
    definition: "something that makes something else happen",
    example: "Smoking is a leading cause of lung cancer."
  },
  {
    word: "caution",
    phonetic: "/ˈkɔːʃən/",
    definition: "great care that you take to avoid possible danger",
    example: "The sign warned of the danger with a note of caution."
  },
  {
    word: "cautious",
    phonetic: "/ˈkɔːʃəs/",
    definition: "taking great care to avoid possible danger",
    example: "She was cautious about giving out her personal information."
  },
  {
    word: "cave",
    phonetic: "/keɪv/",
    definition: "a large hole in the side of a hill or mountain",
    example: "The explorers discovered ancient paintings in the cave."
  },
  {
    word: "cease",
    phonetic: "/siːs/",
    definition: "to stop happening or existing",
    example: "The rain ceased after three days."
  },
  {
    word: "ceiling",
    phonetic: "/ˈsiːlɪŋ/",
    definition: "the flat surface that forms the top part of a room",
    example: "The ceiling of the cathedral is decorated with beautiful paintings."
  },
  {
    word: "celebrate",
    phonetic: "/ˈselɪbreɪt/",
    definition: "to do something special to show that an occasion is important",
    example: "We're going to celebrate our anniversary with a special dinner."
  },
  {
    word: "cell",
    phonetic: "/sel/",
    definition: "the smallest unit of living matter that can exist on its own",
    example: "The human body is made up of billions of cells."
  },
  {
    word: "cellar",
    phonetic: "/ˈselə/",
    definition: "a room under the ground floor of a building, used for storing things",
    example: "Wine is often stored in the cellar."
  },
  {
    word: "cement",
    phonetic: "/sɪˈment/",
    definition: "a gray powder that is mixed with water and sand to make concrete",
    example: "The workers are using cement to build the foundation."
  },
  {
    word: "census",
    phonetic: "/ˈsensəs/",
    definition: "an official count of the people who live in a country",
    example: "The government conducts a census every ten years."
  },
  {
    word: "cent",
    phonetic: "/sent/",
    definition: "a unit of money equal to 1/100 of a dollar or euro",
    example: "The candy costs 50 cents."
  },
  {
    word: "center",
    phonetic: "/ˈsentə/",
    definition: "the middle point or part of something",
    example: "The shopping center is located in the center of town."
  },
  {
    word: "century",
    phonetic: "/ˈsentʃəri/",
    definition: "a period of 100 years",
    example: "The Great Wall of China was built over several centuries."
  },
  {
    word: "ceremony",
    phonetic: "/ˈserəməni/",
    definition: "a formal event that is performed on an important social or religious occasion",
    example: "The wedding ceremony was held in a beautiful church."
  },
  {
    word: "certain",
    phonetic: "/ˈsɜːtn/",
    definition: "having no doubt about something",
    example: "I'm certain that I locked the door."
  },
  {
    word: "certificate",
    phonetic: "/səˈtɪfɪkət/",
    definition: "an official document that shows that something is true or has happened",
    example: "She received a certificate of achievement for her excellent work."
  },
  {
    word: "chain",
    phonetic: "/tʃeɪn/",
    definition: "a series of connected metal rings used for fastening or pulling things",
    example: "The dog was tied to a tree with a chain."
  },
  {
    word: "chair",
    phonetic: "/tʃeə/",
    definition: "a piece of furniture for sitting on, with a back and four legs",
    example: "Please take a chair and make yourself comfortable."
  },
  {
    word: "chairman",
    phonetic: "/ˈtʃeəmən/",
    definition: "the person who is in charge of a meeting or organization",
    example: "The chairman called the meeting to order."
  },
  {
    word: "chalk",
    phonetic: "/tʃɔːk/",
    definition: "a stick of soft white rock used for writing or drawing on a blackboard",
    example: "The teacher wrote the lesson on the blackboard with chalk."
  },
  {
    word: "challenge",
    phonetic: "/ˈtʃælɪndʒ/",
    definition: "a difficult task or situation that tests someone's abilities",
    example: "Learning a new language is a challenge, but it's also rewarding."
  },
  {
    word: "chamber",
    phonetic: "/ˈtʃeɪmbə/",
    definition: "a large room used for a special purpose",
    example: "The musicians rehearsed in the concert chamber."
  },
  {
    word: "champion",
    phonetic: "/ˈtʃæmpiən/",
    definition: "a person or team that has won a competition",
    example: "He is a former Olympic champion."
  },
  {
    word: "chance",
    phonetic: "/tʃɑːns/",
    definition: "the possibility that something will happen",
    example: "There's a good chance that it will rain tomorrow."
  },
  {
    word: "change",
    phonetic: "/tʃeɪndʒ/",
    definition: "to become different, or to make something different",
    example: "The weather changes quickly in the mountains."
  },
  {
    word: "channel",
    phonetic: "/ˈtʃænl/",
    definition: "a television or radio station",
    example: "What's your favorite TV channel?"
  },
  {
    word: "chaos",
    phonetic: "/ˈkeɪɒs/",
    definition: "a state of complete confusion and lack of order",
    example: "The traffic was in chaos after the accident."
  },
  {
    word: "chap",
    phonetic: "/tʃæp/",
    definition: "a man or boy",
    example: "He's a good chap, always willing to help."
  },
  {
    word: "chapter",
    phonetic: "/ˈtʃæptə/",
    definition: "a part of a book that deals with a particular subject",
    example: "I've read the first chapter of the novel."
  },
  {
    word: "character",
    phonetic: "/ˈkærəktə/",
    definition: "the qualities that make someone or something different from others",
    example: "He has a strong character and never gives up."
  },
  {
    word: "characteristic",
    phonetic: "/ˌkærəktəˈrɪstɪk/",
    definition: "a feature or quality that is typical of someone or something",
    example: "One characteristic of the desert is extreme heat during the day."
  },
  {
    word: "charge",
    phonetic: "/tʃɑːdʒ/",
    definition: "the amount of money that you have to pay for something",
    example: "The charge for parking is 10 yuan per hour."
  },
  {
    word: "charity",
    phonetic: "/ˈtʃærəti/",
    definition: "an organization that gives money, food, or help to people who need it",
    example: "She works for a charity that helps homeless people."
  },
  {
    word: "chart",
    phonetic: "/tʃɑːt/",
    definition: "a diagram or graph that shows information",
    example: "The chart shows the company's profits over the last five years."
  },
  {
    word: "chase",
    phonetic: "/tʃeɪs/",
    definition: "to run after someone or something in order to catch them",
    example: "The dog chased the cat up a tree."
  },
  {
    word: "cheat",
    phonetic: "/tʃiːt/",
    definition: "to act in a dishonest way in order to get what you want",
    example: "He was caught cheating in the exam."
  },
  {
    word: "check",
    phonetic: "/tʃek/",
    definition: "to look at something to make sure that it is correct or safe",
    example: "Please check your answers before handing in the test."
  },
  {
    word: "cheek",
    phonetic: "/tʃiːk/",
    definition: "the soft part of your face below your eye",
    example: "She kissed him on the cheek."
  },
  {
    word: "cheer",
    phonetic: "/tʃɪə/",
    definition: "to shout loudly to show support or happiness",
    example: "The crowd cheered when the team scored a goal."
  },
  {
    word: "cheerful",
    phonetic: "/ˈtʃɪəfl/",
    definition: "happy and positive",
    example: "She's always cheerful, even when things go wrong."
  },
  {
    word: "cheese",
    phonetic: "/tʃiːz/",
    definition: "a food made from milk that can be eaten in many different forms",
    example: "Would you like some cheese with your crackers?"
  },
  {
    word: "chemical",
    phonetic: "/ˈkemɪkl/",
    definition: "relating to chemistry or the substances used in chemistry",
    example: "The factory produces various chemical products."
  },
  {
    word: "chemist",
    phonetic: "/ˈkemɪst/",
    definition: "a person who studies chemistry or works with chemicals",
    example: "The chemist analyzed the water sample for pollutants."
  },
  {
    word: "chemistry",
    phonetic: "/ˈkemɪstri/",
    definition: "the scientific study of the structure of substances and how they react with each other",
    example: "She's studying chemistry at university."
  },
  {
    word: "cheque",
    phonetic: "/tʃek/",
    definition: "a piece of paper that you write an amount of money on and sign",
    example: "He wrote a cheque for 500 yuan."
  },
  {
    word: "cherry",
    phonetic: "/ˈtʃeri/",
    definition: "a small, round, red or black fruit with a stone inside",
    example: "The cherry trees are in bloom."
  },
  {
    word: "chess",
    phonetic: "/tʃes/",
    definition: "a game for two players in which each player moves 16 pieces according to fixed rules",
    example: "They often play chess in the park."
  },
  {
    word: "chest",
    phonetic: "/tʃest/",
    definition: "the front part of your body between your neck and your stomach",
    example: "He has a tattoo on his chest."
  },
  {
    word: "chew",
    phonetic: "/tʃuː/",
    definition: "to bite and grind food in your mouth with your teeth",
    example: "You should chew your food thoroughly before swallowing."
  },
  {
    word: "chicken",
    phonetic: "/ˈtʃɪkɪn/",
    definition: "a type of bird that is kept on a farm for its eggs and meat",
    example: "We're having roast chicken for dinner."
  },
  {
    word: "chief",
    phonetic: "/tʃiːf/",
    definition: "the most important person in a group or organization",
    example: "The chief of police held a press conference."
  },
  {
    word: "child",
    phonetic: "/tʃaɪld/",
    definition: "a young human being who is not yet an adult",
    example: "The children are playing in the garden."
  },
  {
    word: "childhood",
    phonetic: "/ˈtʃaɪldhʊd/",
    definition: "the time when you are a child",
    example: "She has happy memories of her childhood."
  },
  {
    word: "chill",
    phonetic: "/tʃɪl/",
    definition: "a feeling of cold",
    example: "There's a chill in the air today."
  },
  {
    word: "chimney",
    phonetic: "/ˈtʃɪmni/",
    definition: "a pipe through which smoke goes up from a fire",
    example: "Smoke was coming out of the chimney."
  },
  {
    word: "chin",
    phonetic: "/tʃɪn/",
    definition: "the part of your face below your mouth",
    example: "He has a beard on his chin."
  },
  {
    word: "china",
    phonetic: "/ˈtʃaɪnə/",
    definition: "dishes, cups, and plates made of porcelain",
    example: "She inherited a set of fine china from her grandmother."
  },
  {
    word: "chip",
    phonetic: "/tʃɪp/",
    definition: "a small piece of something, especially food",
    example: "She ate a bag of potato chips."
  },
  {
    word: "chocolate",
    phonetic: "/ˈtʃɒklət/",
    definition: "a sweet brown food made from cocoa beans",
    example: "She gave him a box of chocolates for his birthday."
  },
  {
    word: "choice",
    phonetic: "/tʃɔɪs/",
    definition: "the act of choosing between two or more possibilities",
    example: "It was a difficult choice, but she decided to accept the job offer."
  },
  {
    word: "choke",
    phonetic: "/tʃəʊk/",
    definition: "to be unable to breathe because something is blocking your throat",
    example: "He choked on a piece of food and had to be given first aid."
  },
  {
    word: "choose",
    phonetic: "/tʃuːz/",
    definition: "to decide which one of a number of things or people you want",
    example: "She chose the red dress for the party."
  },
  {
    word: "chop",
    phonetic: "/tʃɒp/",
    definition: "to cut something into pieces with an axe, knife, or other sharp tool",
    example: "He chopped wood for the fire."
  },
  {
    word: "chorus",
    phonetic: "/ˈkɔːrəs/",
    definition: "a group of people who sing together",
    example: "The choir sang the chorus in harmony."
  },
  {
    word: "christian",
    phonetic: "/ˈkrɪstʃən/",
    definition: "a person who believes in Jesus Christ and follows his teachings",
    example: "She's a devout Christian and goes to church every Sunday."
  },
  {
    word: "Christmas",
    phonetic: "/ˈkrɪsməs/",
    definition: "a Christian festival celebrating the birth of Jesus Christ",
    example: "We exchange gifts at Christmas."
  },
  {
    word: "church",
    phonetic: "/tʃɜːtʃ/",
    definition: "a building where Christians go to worship",
    example: "The church is located in the center of town."
  },
  {
    word: "cigarette",
    phonetic: "/ˌsɪɡəˈret/",
    definition: "a small tube of paper filled with tobacco that people smoke",
    example: "He smoked a cigarette while waiting for the bus."
  },
  {
    word: "cinema",
    phonetic: "/ˈsɪnəmə/",
    definition: "a building where films are shown",
    example: "Let's go to the cinema to see the new James Bond film."
  },
  {
    word: "circle",
    phonetic: "/ˈsɜːkl/",
    definition: "a round shape like a ring",
    example: "The children sat in a circle around the teacher."
  },
  {
    word: "circuit",
    phonetic: "/ˈsɜːkɪt/",
    definition: "a closed path along which electricity flows",
    example: "The electrician checked the circuit for faults."
  },
  {
    word: "circular",
    phonetic: "/ˈsɜːkjʊlə/",
    definition: "shaped like a circle",
    example: "The table has a circular top."
  },
  {
    word: "circulate",
    phonetic: "/ˈsɜːkjʊleɪt/",
    definition: "to move around a place or system",
    example: "Blood circulates through the body."
  },
  {
    word: "circumference",
    phonetic: "/səˈkʌmfərəns/",
    definition: "the distance around the edge of a circle",
    example: "The circumference of a circle can be calculated using the formula 2πr."
  },
  {
    word: "circumstance",
    phonetic: "/ˈsɜːkəmstæns/",
    definition: "the conditions or facts that affect a situation",
    example: "Under normal circumstances, I would agree with you."
  },
  {
    word: "cite",
    phonetic: "/saɪt/",
    definition: "to mention something as an example or proof",
    example: "The author cited several studies to support his argument."
  },
  {
    word: "citizen",
    phonetic: "/ˈsɪtɪzən/",
    definition: "a person who has the right to live in a particular country",
    example: "He is a British citizen."
  },
  {
    word: "city",
    phonetic: "/ˈsɪti/",
    definition: "a large town with many buildings, shops, and people",
    example: "Shanghai is a modern city with a population of over 24 million."
  },
  {
    word: "civil",
    phonetic: "/ˈsɪvl/",
    definition: "relating to the people who live in a country",
    example: "The civil war lasted for five years."
  },
  {
    word: "civilization",
    phonetic: "/ˌsɪvəlaɪˈzeɪʃən/",
    definition: "a society that has developed a high level of culture and organization",
    example: "Ancient Egyptian civilization is famous for its pyramids."
  },
  {
    word: "civilize",
    phonetic: "/ˈsɪvəlaɪz/",
    definition: "to make someone more polite and behave in a more socially acceptable way",
    example: "Education helps to civilize people."
  },
  {
    word: "claim",
    phonetic: "/kleɪm/",
    definition: "to say that something is true, even though it has not been proved",
    example: "He claims to have seen a UFO."
  },
  {
    word: "clap",
    phonetic: "/klæp/",
    definition: "to hit your hands together to show that you like something",
    example: "The audience clapped loudly at the end of the performance."
  },
  {
    word: "clarify",
    phonetic: "/ˈklærəfaɪ/",
    definition: "to make something clearer or easier to understand",
    example: "Could you clarify what you mean by that?"
  },
  {
    word: "clash",
    phonetic: "/klæʃ/",
    definition: "to fight or argue with someone",
    example: "The two teams clashed in a heated argument."
  },
  {
    word: "clasp",
    phonetic: "/klɑːsp/",
    definition: "to hold something or someone tightly",
    example: "She clasped her hands together in prayer."
  },
  {
    word: "class",
    phonetic: "/klɑːs/",
    definition: "a group of students who are taught together",
    example: "Our class has 30 students."
  },
  {
    word: "classic",
    phonetic: "/ˈklæsɪk/",
    definition: "very good and having a value that lasts for a long time",
    example: "Pride and Prejudice is a classic novel."
  },
  {
    word: "classical",
    phonetic: "/ˈklæsɪkl/",
    definition: "relating to ancient Greek and Roman culture, or to music that is considered serious and traditional",
    example: "She enjoys listening to classical music."
  },
  {
    word: "classification",
    phonetic: "/ˌklæsɪfɪˈkeɪʃən/",
    definition: "the act of putting things into groups according to their type",
    example: "The classification of plants is based on their characteristics."
  },
  {
    word: "classify",
    phonetic: "/ˈklæsɪfaɪ/",
    definition: "to put things into groups according to their type",
    example: "Books in the library are classified by subject."
  },
  {
    word: "classmate",
    phonetic: "/ˈklɑːsmeɪt/",
    definition: "someone who is in the same class as you at school or college",
    example: "I've known my classmate since we were in primary school."
  },
  {
    word: "classroom",
    phonetic: "/ˈklɑːsruːm/",
    definition: "a room where lessons are taught",
    example: "The classroom was bright and airy."
  },
  {
    word: "claw",
    phonetic: "/klɔː/",
    definition: "the sharp curved nail on the foot of an animal or bird",
    example: "The cat sharpened its claws on the tree."
  },
  {
    word: "clay",
    phonetic: "/kleɪ/",
    definition: "a type of earth that is soft when wet and hard when baked",
    example: "Pottery is made from clay."
  },
  {
    word: "clean",
    phonetic: "/kliːn/",
    definition: "free from dirt or marks",
    example: "Please keep the classroom clean."
  },
  {
    word: "clear",
    phonetic: "/klɪə/",
    definition: "easy to see, hear, or understand",
    example: "The instructions are clear and easy to follow."
  },
  {
    word: "clerk",
    phonetic: "/klɑːk/",
    definition: "a person who works in an office, dealing with records or performing general office duties",
    example: "The bank clerk helped me open a new account."
  },
  {
    word: "clever",
    phonetic: "/ˈklevə/",
    definition: "intelligent and able to learn things quickly",
    example: "She's a clever student who always gets good grades."
  },
  {
    word: "cliff",
    phonetic: "/klɪf/",
    definition: "a high area of rock with a very steep side, often at the edge of the sea or a river",
    example: "The castle was built on top of a cliff."
  },
  {
    word: "climb",
    phonetic: "/klaɪm/",
    definition: "to move up or down something using your hands and feet",
    example: "We climbed to the top of the mountain."
  },
  {
    word: "clinic",
    phonetic: "/ˈklɪnɪk/",
    definition: "a place where people go to receive medical treatment",
    example: "She works at a dental clinic."
  },
  {
    word: "clip",
    phonetic: "/klɪp/",
    definition: "a small object used for holding things together",
    example: "She used a clip to keep her papers together."
  },
  {
    word: "cloak",
    phonetic: "/kləʊk/",
    definition: "a long, loose outer garment without sleeves",
    example: "The knight wore a cloak over his armor."
  },
  {
    word: "clock",
    phonetic: "/klɒk/",
    definition: "a device used for measuring and showing time",
    example: "The clock on the wall shows the correct time."
  },
  {
    word: "clone",
    phonetic: "/kləʊn/",
    definition: "an exact copy of a plant or animal that is produced from one cell of the original",
    example: "Scientists have cloned sheep and other animals."
  },
  {
    word: "close",
    phonetic: "/kləʊz/",
    definition: "to shut something",
    example: "Please close the door when you leave."
  },
  {
    word: "cloth",
    phonetic: "/klɒθ/",
    definition: "material made from threads, used for making clothes, curtains, etc.",
    example: "She bought some cloth to make a dress."
  },
  {
    word: "clothe",
    phonetic: "/kləʊð/",
    definition: "to provide someone with clothes",
    example: "The charity helps to clothe homeless people."
  },
  {
    word: "clothes",
    phonetic: "/kləʊðz/",
    definition: "things that you wear, such as shirts, pants, dresses, etc.",
    example: "She packed her clothes for the trip."
  },
  {
    word: "clothing",
    phonetic: "/ˈkləʊðɪŋ/",
    definition: "clothes, especially when considered as a group",
    example: "The store sells a wide range of outdoor clothing."
  },
  {
    word: "cloud",
    phonetic: "/klaʊd/",
    definition: "a white or gray mass in the sky that is made of very small drops of water",
    example: "The sky was filled with dark clouds."
  },
  {
    word: "cloudy",
    phonetic: "/ˈklaʊdi/",
    definition: "covered with clouds",
    example: "It's cloudy today, so we can't see the sun."
  },
  {
    word: "club",
    phonetic: "/klʌb/",
    definition: "an organization for people who share a particular interest or activity",
    example: "He's a member of the photography club."
  },
  {
    word: "clue",
    phonetic: "/kluː/",
    definition: "a piece of information that helps you solve a problem or mystery",
    example: "The detective found an important clue at the crime scene."
  },
  {
    word: "clumsy",
    phonetic: "/ˈklʌmzi/",
    definition: "moving or doing things in a way that is not careful or graceful",
    example: "He's very clumsy and always dropping things."
  },
  {
    word: "coach",
    phonetic: "/kəʊtʃ/",
    definition: "a person who trains and teaches a sports team or performer",
    example: "The football coach gave the team a pep talk before the game."
  },
  {
    word: "coal",
    phonetic: "/kəʊl/",
    definition: "a black substance that is dug from the ground and burned to produce heat",
    example: "The power station burns coal to generate electricity."
  },
  {
    word: "coast",
    phonetic: "/kəʊst/",
    definition: "the land along the edge of the sea",
    example: "They spent their vacation on the coast."
  },
  {
    word: "coat",
    phonetic: "/kəʊt/",
    definition: "a piece of clothing with sleeves that you wear over other clothes to keep warm",
    example: "She put on her coat before going outside."
  },
  {
    word: "cock",
    phonetic: "/kɒk/",
    definition: "a male chicken",
    example: "The cock crows at dawn."
  },
  {
    word: "code",
    phonetic: "/kəʊd/",
    definition: "a system of words, letters, or symbols that is used to represent something",
    example: "The message was written in code."
  },
  {
    word: "coffee",
    phonetic: "/ˈkɒfi/",
    definition: "a hot drink made from ground coffee beans",
    example: "Would you like a cup of coffee?"
  },
  {
    word: "cognitive",
    phonetic: "/ˈkɒɡnətɪv/",
    definition: "relating to the process of knowing, understanding, and learning something",
    example: "The test measures cognitive abilities such as memory and reasoning."
  },
  {
    word: "coherent",
    phonetic: "/kəʊˈhɪərənt/",
    definition: "logical and well organized",
    example: "His explanation was clear and coherent."
  },
  {
    word: "coil",
    phonetic: "/kɔɪl/",
    definition: "a length of rope, wire, etc., that has been wrapped around into a series of circles",
    example: "The snake coiled itself around the branch."
  },
  {
    word: "coin",
    phonetic: "/kɔɪn/",
    definition: "a small, flat, round piece of metal used as money",
    example: "He found a coin on the street."
  },
  {
    word: "coincidence",
    phonetic: "/kəʊˈɪnsɪdəns/",
    definition: "the fact of two things happening at the same time by chance",
    example: "It was a coincidence that we met again after so many years."
  },
  {
    word: "coke",
    phonetic: "/kəʊk/",
    definition: "a solid black substance that is left after coal has been heated and that is used as fuel",
    example: "The steel industry uses coke in the production process."
  },
  {
    word: "cold",
    phonetic: "/kəʊld/",
    definition: "having a low temperature",
    example: "It's very cold outside today."
  },
  {
    word: "collar",
    phonetic: "/ˈkɒlə/",
    definition: "the part of a shirt or dress that goes around your neck",
    example: "He buttoned his collar before putting on his tie."
  },
  {
    word: "collapse",
    phonetic: "/kəˈlæps/",
    definition: "to fall down or fall apart suddenly",
    example: "The old building collapsed during the earthquake."
  },
  {
    word: "collarborate",
    phonetic: "/kəˈlæbəreɪt/",
    definition: "to work together with someone to achieve something",
    example: "Scientists from different countries collaborated on the research project."
  },
  {
    word: "collapse",
    phonetic: "/kəˈlæps/",
    definition: "to fall down or fall apart suddenly",
    example: "The bridge collapsed under the weight of the truck."
  },
  {
    word: "colleague",
    phonetic: "/ˈkɒliːɡ/",
    definition: "someone that you work with",
    example: "Her colleagues gave her a present when she retired."
  },
  {
    word: "collect",
    phonetic: "/kəˈlekt/",
    definition: "to bring things together from different places",
    example: "She collects stamps from all over the world."
  },
  {
    word: "collection",
    phonetic: "/kəˈlekʃən/",
    definition: "a group of similar things that have been collected",
    example: "The museum has a large collection of ancient artifacts."
  },
  {
    word: "collective",
    phonetic: "/kəˈlektɪv/",
    definition: "shared or done by a group of people",
    example: "The team made a collective decision to postpone the project."
  },
  {
    word: "college",
    phonetic: "/ˈkɒlɪdʒ/",
    definition: "a place where students study after high school",
    example: "She's studying English literature at college."
  },
  {
    word: "collision",
    phonetic: "/kəˈlɪʒən/",
    definition: "an accident in which two vehicles hit each other",
    example: "There was a collision between two cars at the intersection."
  },
  {
    word: "colonel",
    phonetic: "/ˈkɜːnl/",
    definition: "an officer of high rank in the army, air force, or marines",
    example: "The colonel gave orders to his troops."
  },
  {
    word: "colony",
    phonetic: "/ˈkɒləni/",
    definition: "a country or area that is controlled by another country",
    example: "Australia was once a British colony."
  },
  {
    word: "color",
    phonetic: "/ˈkʌlə/",
    definition: "the appearance that things have that results from the way they reflect light",
    example: "What's your favorite color?"
  },
  {
    word: "column",
    phonetic: "/ˈkɒləm/",
    definition: "a tall, vertical structure that supports a building",
    example: "The ancient temple has many stone columns."
  },
  {
    word: "comb",
    phonetic: "/kəʊm/",
    definition: "a flat piece of plastic or metal with teeth that is used for making hair neat",
    example: "She used a comb to brush her hair."
  },
  {
    word: "combine",
    phonetic: "/kəmˈbaɪn/",
    definition: "to join together to form a single thing or group",
    example: "The two companies combined to form a new corporation."
  },
  {
    word: "come",
    phonetic: "/kʌm/",
    definition: "to move towards or arrive at a place",
    example: "Please come to my office when you're free."
  },
  {
    word: "comedy",
    phonetic: "/ˈkɒmədi/",
    definition: "a play, film, or television program that is intended to make people laugh",
    example: "We watched a comedy last night and laughed a lot."
  },
  {
    word: "comfort",
    phonetic: "/ˈkʌmfət/",
    definition: "a state of being physically relaxed and free from pain",
    example: "The soft chair provided great comfort."
  },
  {
    word: "comfortable",
    phonetic: "/ˈkʌmftəbl/",
    definition: "giving a feeling of physical comfort",
    example: "The bed is very comfortable."
  },
  {
    word: "command",
    phonetic: "/kəˈmɑːnd/",
    definition: "an order given by someone in authority",
    example: "The general gave the command to attack."
  },
  {
    word: "commander",
    phonetic: "/kəˈmɑːndə/",
    definition: "an officer in the armed forces who is in charge of a group of soldiers",
    example: "The commander led his troops into battle."
  },
  {
    word: "comment",
    phonetic: "/ˈkɒment/",
    definition: "something that you say or write that gives your opinion about something",
    example: "She made a comment about the weather."
  },
  {
    word: "commerce",
    phonetic: "/ˈkɒmɜːs/",
    definition: "the activity of buying and selling goods and services",
    example: "International commerce has increased in recent years."
  },
  {
    word: "commercial",
    phonetic: "/kəˈmɜːʃl/",
    definition: "relating to business or commerce",
    example: "The city has a busy commercial district."
  },
  {
    word: "commission",
    phonetic: "/kəˈmɪʃən/",
    definition: "an amount of money paid to someone for selling goods or services",
    example: "The salesperson earns a 10% commission on each sale."
  },
  {
    word: "commit",
    phonetic: "/kəˈmɪt/",
    definition: "to do something illegal or wrong",
    example: "He was arrested for committing a robbery."
  },
  {
    word: "committee",
    phonetic: "/kəˈmɪti/",
    definition: "a group of people who are chosen to do a particular job",
    example: "The committee is responsible for organizing the event."
  },
  {
    word: "common",
    phonetic: "/ˈkɒmən/",
    definition: "happening often or existing in many places",
    example: "Colds are common in winter."
  },
  {
    word: "communicate",
    phonetic: "/kəˈmjuːnɪkeɪt/",
    definition: "to share information or ideas with someone",
    example: "It's important to communicate clearly with your colleagues."
  },
  {
    word: "communication",
    phonetic: "/kəˈmjuːnɪkeɪʃən/",
    definition: "the process of sharing information or ideas",
    example: "Good communication is essential in any relationship."
  },
  {
    word: "communism",
    phonetic: "/ˈkɒmjʊnɪzəm/",
    definition: "a political system in which the government owns all property and everyone is equal",
    example: "Communism was the official ideology of the Soviet Union."
  },
  {
    word: "communist",
    phonetic: "/ˈkɒmjʊnɪst/",
    definition: "someone who believes in communism",
    example: "The country was ruled by a communist government."
  },
  {
    word: "community",
    phonetic: "/kəˈmjuːnəti/",
    definition: "a group of people who live in the same area or have the same interests",
    example: "The local community organized a charity event."
  },
  {
    word: "companion",
    phonetic: "/kəmˈpæniən/",
    definition: "a person who spends time with you",
    example: "She was a faithful companion to him in his old age."
  },
  {
    word: "company",
    phonetic: "/ˈkʌmpəni/",
    definition: "a business organization that makes or sells goods or services",
    example: "She works for a software company."
  },
  {
    word: "comparable",
    phonetic: "/ˈkɒmpərəbl/",
    definition: "similar to something else in size, quality, or importance",
    example: "The two products are comparable in price."
  },
  {
    word: "comparative",
    phonetic: "/kəmˈpærətɪv/",
    definition: "relating to comparison",
    example: "The comparative study of different cultures is interesting."
  },
  {
    word: "compare",
    phonetic: "/kəmˈpeə/",
    definition: "to examine two or more things in order to see how they are similar or different",
    example: "Compare these two pictures and tell me what's different."
  },
  {
    word: "comparison",
    phonetic: "/kəmˈpærɪsn/",
    definition: "the act of comparing two or more things",
    example: "By comparison, this book is much better than the last one."
  },
  {
    word: "compel",
    phonetic: "/kəmˈpel/",
    definition: "to force someone to do something",
    example: "The law compels parents to send their children to school."
  },
  {
    word: "compensate",
    phonetic: "/ˈkɒmpenseɪt/",
    definition: "to pay someone money because they have suffered a loss or injury",
    example: "The company compensated him for the injury he suffered at work."
  },
  {
    word: "compete",
    phonetic: "/kəmˈpiːt/",
    definition: "to try to win something or be more successful than others",
    example: "Several companies are competing for the contract."
  },
  {
    word: "competent",
    phonetic: "/ˈkɒmpɪtənt/",
    definition: "having enough skill or knowledge to do something well",
    example: "He is a competent driver."
  },
  {
    word: "competition",
    phonetic: "/ˌkɒmpəˈtɪʃən/",
    definition: "a situation in which people or organizations try to be more successful than others",
    example: "There is fierce competition in the smartphone market."
  },
  {
    word: "competitive",
    phonetic: "/kəmˈpetɪtɪv/",
    definition: "wanting to be more successful than others",
    example: "She has a competitive nature and always wants to win."
  },
  {
    word: "compile",
    phonetic: "/kəmˈpaɪl/",
    definition: "to collect information from different places and arrange it in a book, report, etc.",
    example: "He compiled a dictionary of local dialects."
  },
  {
    word: "complaint",
    phonetic: "/kəmˈpleɪnt/",
    definition: "a statement that you are not satisfied with something",
    example: "The customer made a complaint about the service."
  },
  {
    word: "complement",
    phonetic: "/ˈkɒmplɪment/",
    definition: "something that makes something else better or more complete",
    example: "The wine was a perfect complement to the meal."
  },
  {
    word: "complete",
    phonetic: "/kəmˈpliːt/",
    definition: "having all the necessary parts",
    example: "The project is now complete."
  },
  {
    word: "complex",
    phonetic: "/ˈkɒmpleks/",
    definition: "difficult to understand or deal with",
    example: "The problem is more complex than I thought."
  },
  {
    word: "complicated",
    phonetic: "/ˈkɒmplɪkeɪtɪd/",
    definition: "difficult to understand or explain",
    example: "The instructions are very complicated."
  },
  {
    word: "component",
    phonetic: "/kəmˈpəʊnənt/",
    definition: "a part of a machine or system",
    example: "The engine has several important components."
  },
  {
    word: "compose",
    phonetic: "/kəmˈpəʊz/",
    definition: "to write music, poetry, or a piece of writing",
    example: "He composed a symphony when he was only 18."
  },
  {
    word: "composition",
    phonetic: "/ˌkɒmpəˈzɪʃən/",
    definition: "a piece of music, poetry, or writing",
    example: "She wrote a composition about her summer vacation."
  },
  {
    word: "compound",
    phonetic: "/ˈkɒmpaʊnd/",
    definition: "a substance formed by a chemical reaction of two or more elements",
    example: "Water is a compound made up of hydrogen and oxygen."
  },
  {
    word: "comprehend",
    phonetic: "/ˌkɒmprɪˈhend/",
    definition: "to understand something",
    example: "I can't comprehend why he would do such a thing."
  },
  {
    word: "comprehensive",
    phonetic: "/ˌkɒmprɪˈhensɪv/",
    definition: "including all the necessary facts, details, or problems",
    example: "The book provides a comprehensive overview of the subject."
  },
  {
    word: "compress",
    phonetic: "/kəmˈpres/",
    definition: "to press something into a smaller space",
    example: "The files were compressed to save space."
  },
  {
    word: "comprise",
    phonetic: "/kəmˈpraɪz/",
    definition: "to consist of particular parts or members",
    example: "The committee comprises five members."
  },
  {
    word: "compromise",
    phonetic: "/ˈkɒmprəmaɪz/",
    definition: "an agreement in which people accept less than what they want",
    example: "They reached a compromise after hours of negotiation."
  },
  {
    word: "compulsory",
    phonetic: "/kəmˈpʌlsəri/",
    definition: "that must be done because of a law or rule",
    example: "Attendance at school is compulsory for children between 5 and 16."
  },
  {
    word: "compute",
    phonetic: "/kəmˈpjuːt/",
    definition: "to calculate something",
    example: "The computer computed the results in seconds."
  },
  {
    word: "computer",
    phonetic: "/kəmˈpjuːtə/",
    definition: "an electronic machine that can store and process data",
    example: "I need to buy a new computer for my studies."
  },
  {
    word: "comrade",
    phonetic: "/ˈkɒmreɪd/",
    definition: "a friend or companion, especially in a political party or army",
    example: "He fought alongside his comrades in the war."
  },
  {
    word: "conceal",
    phonetic: "/kənˈsiːl/",
    definition: "to hide something",
    example: "She concealed her feelings behind a smile."
  },
  {
    word: "concentrate",
    phonetic: "/ˈkɒnsəntreɪt/",
    definition: "to give all your attention to something",
    example: "I need to concentrate on my studies."
  },
  {
    word: "concentration",
    phonetic: "/ˌkɒnsənˈtreɪʃən/",
    definition: "the ability to give all your attention to something",
    example: "Children have short attention spans and poor concentration."
  },
  {
    word: "concept",
    phonetic: "/ˈkɒnsept/",
    definition: "an idea or principle",
    example: "The concept of democracy is important in modern societies."
  },
  {
    word: "concern",
    phonetic: "/kənˈsɜːn/",
    definition: "a feeling of worry about something",
    example: "There is growing concern about climate change."
  },
  {
    word: "concerning",
    phonetic: "/kənˈsɜːnɪŋ/",
    definition: "about something",
    example: "I have a question concerning your recent article."
  },
  {
    word: "concert",
    phonetic: "/ˈkɒnsət/",
    definition: "a performance of music by musicians or singers",
    example: "We went to a classical music concert last night."
  },
  {
    word: "conclude",
    phonetic: "/kənˈkluːd/",
    definition: "to come to an end",
    example: "The meeting concluded at 5 o'clock."
  },
  {
    word: "conclusion",
    phonetic: "/kənˈkluːʒən/",
    definition: "the end of something",
    example: "We reached the conclusion that we needed to change our strategy."
  },
  {
    word: "concrete",
    phonetic: "/ˈkɒŋkriːt/",
    definition: "a hard building material made by mixing cement, sand, and water",
    example: "The sidewalk is made of concrete."
  },
  {
    word: "condemn",
    phonetic: "/kənˈdem/",
    definition: "to express strong disapproval of something",
    example: "The government condemned the terrorist attack."
  },
  {
    word: "condense",
    phonetic: "/kənˈdens/",
    definition: "to make something shorter or more concentrated",
    example: "The report was condensed into a single page."
  },
  {
    word: "condition",
    phonetic: "/kənˈdɪʃən/",
    definition: "the state that something is in",
    example: "The car is in excellent condition."
  },
  {
    word: "conduct",
    phonetic: "/ˈkɒndʌkt/",
    definition: "the way that someone behaves",
    example: "His conduct at the meeting was inappropriate."
  },
  {
    word: "conductor",
    phonetic: "/kənˈdʌktə/",
    definition: "a person who directs an orchestra or choir",
    example: "The conductor raised his baton and the orchestra began to play."
  },
  {
    word: "conference",
    phonetic: "/ˈkɒnfərəns/",
    definition: "a meeting where people discuss a particular subject",
    example: "She attended an international conference on climate change."
  },
  {
    word: "confess",
    phonetic: "/kənˈfes/",
    definition: "to admit that you have done something wrong",
    example: "He confessed to stealing the money."
  },
  {
    word: "confidence",
    phonetic: "/ˈkɒnfɪdəns/",
    definition: "the feeling that you can trust someone or something",
    example: "She has confidence in her ability to succeed."
  },
  {
    word: "confident",
    phonetic: "/ˈkɒnfɪdənt/",
    definition: "feeling sure about your ability to do something",
    example: "He is confident that he will pass the exam."
  },
  {
    word: "confidential",
    phonetic: "/ˌkɒnfɪˈdenʃl/",
    definition: "meant to be kept secret",
    example: "This information is confidential and should not be shared."
  },
  {
    word: "confine",
    phonetic: "/kənˈfaɪn/",
    definition: "to keep someone or something within limits",
    example: "The dog was confined to the backyard."
  },
  {
    word: "confirm",
    phonetic: "/kənˈfɜːm/",
    definition: "to make sure that something is true",
    example: "Please confirm your reservation by phone."
  },
  {
    word: "conflict",
    phonetic: "/ˈkɒnflɪkt/",
    definition: "a disagreement or argument between two people or groups",
    example: "There was a conflict between the two political parties."
  },
  {
    word: "conform",
    phonetic: "/kənˈfɔːm/",
    definition: "to behave in the way that most people behave",
    example: "He refused to conform to society's expectations."
  },
  {
    word: "confuse",
    phonetic: "/kənˈfjuːz/",
    definition: "to make someone unable to think clearly",
    example: "The instructions confused me."
  },
  {
    word: "confusion",
    phonetic: "/kənˈfjuːʒən/",
    definition: "a state of not being able to think clearly",
    example: "There was confusion after the fire alarm went off."
  },
  {
    word: "congratulate",
    phonetic: "/kənˈɡrætʃuleɪt/",
    definition: "to tell someone that you are happy about their success",
    example: "I congratulated her on her promotion."
  },
  {
    word: "congratulation",
    phonetic: "/kənˌɡrætʃuˈleɪʃən/",
    definition: "an expression of happiness about someone's success",
    example: "Congratulations on your graduation!"
  },
  {
    word: "congress",
    phonetic: "/ˈkɒŋɡres/",
    definition: "a large meeting of people who discuss important matters",
    example: "The annual medical congress will be held in Paris this year."
  },
  {
    word: "conjunction",
    phonetic: "/kənˈdʒʌŋkʃən/",
    definition: "a word that connects words, phrases, or clauses",
    example: "Common conjunctions include 'and', 'but', and 'or'."
  },
  {
    word: "connect",
    phonetic: "/kəˈnekt/",
    definition: "to join or link together",
    example: "The bridge connects the two parts of the city."
  },
  {
    word: "connection",
    phonetic: "/kəˈnekʃən/",
    definition: "a link between two or more things",
    example: "There is a connection between smoking and lung cancer."
  },
  {
    word: "conquer",
    phonetic: "/ˈkɒŋkə/",
    definition: "to take control of a country or city by force",
    example: "The army conquered the enemy's territory."
  },
  {
    word: "conquest",
    phonetic: "/ˈkɒŋkwest/",
    definition: "the act of taking control of a country or city by force",
    example: "The conquest of the New World by European explorers changed history."
  },
  {
    word: "conscience",
    phonetic: "/ˈkɒnʃəns/",
    definition: "the part of your mind that tells you whether your actions are right or wrong",
    example: "His conscience told him that he should apologize."
  },
  {
    word: "conscious",
    phonetic: "/ˈkɒnʃəs/",
    definition: "aware of what is happening around you",
    example: "She was conscious during the operation."
  },
  {
    word: "consciousness",
    phonetic: "/ˈkɒnʃəsnəs/",
    definition: "the state of being aware of what is happening around you",
    example: "He lost consciousness after the accident."
  },
  {
    word: "consent",
    phonetic: "/kənˈsent/",
    definition: "permission to do something",
    example: "He gave his consent for the operation."
  },
  {
    word: "consequence",
    phonetic: "/ˈkɒnsɪkwəns/",
    definition: "a result of something that has happened",
    example: "The consequences of climate change are becoming more apparent."
  },
  {
    word: "consequently",
    phonetic: "/ˈkɒnsɪkwəntli/",
    definition: "as a result",
    example: "He didn't study for the exam and consequently failed."
  },
  {
    word: "conservation",
    phonetic: "/ˌkɒnsəˈveɪʃən/",
    definition: "the protection of natural things such as animals, plants, and forests",
    example: "Conservation efforts have helped to save endangered species."
  },
  {
    word: "conservative",
    phonetic: "/kənˈsɜːvətɪv/",
    definition: "not liking change",
    example: "He has conservative views on social issues."
  },
  {
    word: "consider",
    phonetic: "/kənˈsɪdə/",
    definition: "to think about something carefully",
    example: "Please consider my proposal before making a decision."
  },
  {
    word: "considerable",
    phonetic: "/kənˈsɪdərəbl/",
    definition: "large in amount or degree",
    example: "There has been a considerable improvement in his health."
  },
  {
    word: "considerate",
    phonetic: "/kənˈsɪdərət/",
    definition: "thinking about the needs and feelings of other people",
    example: "It was considerate of him to bring flowers."
  },
  {
    word: "consideration",
    phonetic: "/kənˌsɪdəˈreɪʃən/",
    definition: "the act of thinking about something carefully",
    example: "After careful consideration, I decided to accept the job offer."
  },
  {
    word: "consist",
    phonetic: "/kənˈsɪst/",
    definition: "to be made up of particular parts",
    example: "The team consists of five members."
  },
  {
    word: "consistent",
    phonetic: "/kənˈsɪstənt/",
    definition: "always behaving or happening in a similar way",
    example: "His performance has been consistent throughout the season."
  },
  {
    word: "constant",
    phonetic: "/ˈkɒnstənt/",
    definition: "happening all the time or very often",
    example: "The constant noise from the construction site is annoying."
  },
  {
    word: "constituent",
    phonetic: "/kənˈstɪtjuənt/",
    definition: "a person who lives in an area represented by a particular elected official",
    example: "The senator met with her constituents to discuss their concerns."
  },
  {
    word: "constitute",
    phonetic: "/ˈkɒnstɪtjuːt/",
    definition: "to form or make up something",
    example: "The committee constitutes the governing body of the organization."
  },
  {
    word: "constitution",
    phonetic: "/ˌkɒnstɪˈtjuːʃən/",
    definition: "the system of laws and principles according to which a country is governed",
    example: "The US Constitution was adopted in 1787."
  },
  {
    word: "construct",
    phonetic: "/kənˈstrʌkt/",
    definition: "to build something",
    example: "They are constructing a new bridge across the river."
  },
  {
    word: "construction",
    phonetic: "/kənˈstrʌkʃən/",
    definition: "the process of building something",
    example: "The construction of the new hospital will take two years."
  },
  {
    word: "consult",
    phonetic: "/kənˈsʌlt/",
    definition: "to ask for advice or information from someone",
    example: "I need to consult a doctor about my back pain."
  },
  {
    word: "consultant",
    phonetic: "/kənˈsʌltənt/",
    definition: "a person who gives expert advice on a particular subject",
    example: "The company hired a management consultant to improve efficiency."
  },
  {
    word: "consume",
    phonetic: "/kənˈsjuːm/",
    definition: "to eat or drink something",
    example: "We consumed all the food at the party."
  },
  {
    word: "consumer",
    phonetic: "/kənˈsjuːmə/",
    definition: "a person who buys and uses goods and services",
    example: "Consumers are becoming more aware of environmental issues."
  },
  {
    word: "consumption",
    phonetic: "/kənˈsʌmpʃən/",
    definition: "the act of buying and using goods and services",
    example: "The country's consumption of oil has increased in recent years."
  },
  {
    word: "contact",
    phonetic: "/ˈkɒntækt/",
    definition: "communication with someone",
    example: "Please keep in contact with me while you're away."
  },
  {
    word: "contain",
    phonetic: "/kənˈteɪn/",
    definition: "to have something inside or as part of itself",
    example: "The box contains books and papers."
  },
  {
    word: "container",
    phonetic: "/kənˈteɪnə/",
    definition: "a box, bottle, or other object used for holding something",
    example: "The goods were shipped in large containers."
  },
  {
    word: "contaminate",
    phonetic: "/kənˈtæmɪneɪt/",
    definition: "to make something dirty or poisonous",
    example: "The river was contaminated by industrial waste."
  },
  {
    word: "contemporary",
    phonetic: "/kənˈtempərəri/",
    definition: "belonging to the present time",
    example: "She writes contemporary fiction."
  },
  {
    word: "contempt",
    phonetic: "/kənˈtempt/",
    definition: "a feeling of strong dislike or lack of respect for someone",
    example: "He looked at her with contempt."
  },
  {
    word: "contend",
    phonetic: "/kənˈtend/",
    definition: "to argue or state that something is true",
    example: "Scientists contend that climate change is caused by human activity."
  },
  {
    word: "content",
    phonetic: "/ˈkɒntent/",
    definition: "the things that are written in a book, magazine, or website",
    example: "The content of the book is very interesting."
  },
  {
    word: "contest",
    phonetic: "/ˈkɒntest/",
    definition: "a competition to find out who is the best at something",
    example: "She won first prize in the singing contest."
  },
  {
    word: "context",
    phonetic: "/ˈkɒntekst/",
    definition: "the situation in which something happens",
    example: "The historical context helps to understand the novel."
  },
  {
    word: "continue",
    phonetic: "/kənˈtɪnjuː/",
    definition: "to keep happening or existing",
    example: "The rain continued for three days."
  },
  {
    word: "continuous",
    phonetic: "/kənˈtɪnjuəs/",
    definition: "happening without stopping",
    example: "There was continuous noise from the construction site."
  },
  {
    word: "contract",
    phonetic: "/ˈkɒntrækt/",
    definition: "a written or spoken agreement between two or more people",
    example: "They signed a contract to work together for five years."
  },
  {
    word: "contradict",
    phonetic: "/ˌkɒntrəˈdɪkt/",
    definition: "to say the opposite of what someone else has said",
    example: "His statement contradicts what he said yesterday."
  },
  {
    word: "contrary",
    phonetic: "/ˈkɒntrəri/",
    definition: "the opposite of what has been said or expected",
    example: "Contrary to popular belief, not all cats hate water."
  },
  {
    word: "contrast",
    phonetic: "/ˈkɒntrɑːst/",
    definition: "a difference between people or things that are compared",
    example: "There is a sharp contrast between the two brothers."
  },
  {
    word: "contribute",
    phonetic: "/kənˈtrɪbjuːt/",
    definition: "to give something, especially money or time",
    example: "She contributed $100 to the charity."
  },
  {
    word: "contribution",
    phonetic: "/ˌkɒntrɪˈbjuːʃən/",
    definition: "something that you give or do to help achieve something",
    example: "His contribution to the project was essential."
  },
  {
    word: "control",
    phonetic: "/kənˈtrəʊl/",
    definition: "the power to make someone or something do what you want",
    example: "The government has control over the country's resources."
  },
  {
    word: "controversial",
    phonetic: "/ˌkɒntrəˈvɜːʃl/",
    definition: "causing disagreement or argument",
    example: "The new policy is very controversial."
  },
  {
    word: "controversy",
    phonetic: "/ˈkɒntrəvɜːsi/",
    definition: "a lot of disagreement or argument about something",
    example: "There was a lot of controversy surrounding the decision."
  },
  {
    word: "convenience",
    phonetic: "/kənˈviːniəns/",
    definition: "the quality of being easy to use or do",
    example: "The store is popular because of its convenience."
  },
  {
    word: "convenient",
    phonetic: "/kənˈviːniənt/",
    definition: "easy to use or do",
    example: "The hotel is in a convenient location."
  },
  {
    word: "convention",
    phonetic: "/kənˈvenʃən/",
    definition: "a large meeting of people who have the same interest",
    example: "The annual medical convention will be held in Chicago this year."
  },
  {
    word: "conventional",
    phonetic: "/kənˈvenʃənl/",
    definition: "following what is traditional or normal",
    example: "She has conventional views on marriage."
  },
  {
    word: "conversation",
    phonetic: "/ˌkɒnvəˈseɪʃən/",
    definition: "a talk between two or more people",
    example: "We had a pleasant conversation over dinner."
  },
  {
    word: "converse",
    phonetic: "/kənˈvɜːs/",
    definition: "to talk with someone",
    example: "She conversed with the guests at the party."
  },
  {
    word: "convert",
    phonetic: "/kənˈvɜːt/",
    definition: "to change something into a different form",
    example: "The company converted the old factory into apartments."
  },
  {
    word: "convey",
    phonetic: "/kənˈveɪ/",
    definition: "to communicate or express something",
    example: "The painting conveys a sense of peace and tranquility."
  },
  {
    word: "convict",
    phonetic: "/kənˈvɪkt/",
    definition: "to declare someone guilty of a crime",
    example: "He was convicted of murder and sentenced to life in prison."
  },
  {
    word: "conviction",
    phonetic: "/kənˈvɪkʃən/",
    definition: "a strong belief or opinion",
    example: "She has strong convictions about environmental protection."
  },
  {
    word: "convince",
    phonetic: "/kənˈvɪns/",
    definition: "to make someone believe that something is true",
    example: "I couldn't convince him to change his mind."
  },
  {
    word: "convincing",
    phonetic: "/kənˈvɪnsɪŋ/",
    definition: "making someone believe that something is true",
    example: "She gave a convincing argument for her proposal."
  },
  {
    word: "cook",
    phonetic: "/kʊk/",
    definition: "to prepare food by heating it",
    example: "She cooks dinner for her family every night."
  },
  {
    word: "cool",
    phonetic: "/kuːl/",
    definition: "slightly cold",
    example: "The weather is cool today."
  },
  {
    word: "cooperate",
    phonetic: "/kəʊˈɒpəreɪt/",
    definition: "to work together with someone",
    example: "The two companies agreed to cooperate on the project."
  },
  {
    word: "cooperation",
    phonetic: "/kəʊˌɒpəˈreɪʃən/",
    definition: "the act of working together with someone",
    example: "Cooperation between the two countries has improved."
  },
  {
    word: "coordinate",
    phonetic: "/kəʊˈɔːdɪneɪt/",
    definition: "to organize the different parts of an activity",
    example: "She coordinates the company's marketing campaigns."
  },
  {
    word: "cop",
    phonetic: "/kɒp/",
    definition: "a police officer",
    example: "The cop asked for his driver's license."
  },
  {
    word: "cope",
    phonetic: "/kəʊp/",
    definition: "to deal successfully with a difficult situation",
    example: "She's coping well with the pressure of her new job."
  },
  {
    word: "copper",
    phonetic: "/ˈkɒpə/",
    definition: "a reddish-brown metal that is used to make electrical wires",
    example: "The statue is made of copper."
  },
  {
    word: "copy",
    phonetic: "/ˈkɒpi/",
    definition: "a thing that is made to be exactly like another thing",
    example: "I made a copy of the document for you."
  },
  {
    word: "copyright",
    phonetic: "/ˈkɒpiraɪt/",
    definition: "the legal right to control the production and sale of a book, play, film, etc.",
    example: "The book is protected by copyright."
  },
  {
    word: "cord",
    phonetic: "/kɔːd/",
    definition: "a thick string or rope",
    example: "He tied the package with a cord."
  },
  {
    word: "core",
    phonetic: "/kɔː/",
    definition: "the central or most important part of something",
    example: "The core of the problem is a lack of communication."
  },
  {
    word: "corn",
    phonetic: "/kɔːn/",
    definition: "a tall plant that produces yellow seeds that are eaten as food",
    example: "Corn is a major crop in the Midwest."
  },
  {
    word: "corner",
    phonetic: "/ˈkɔːnə/",
    definition: "the point where two lines or surfaces meet",
    example: "The cat is sitting in the corner of the room."
  },
  {
    word: "corporation",
    phonetic: "/ˌkɔːpəˈreɪʃən/",
    definition: "a large company or group of companies",
    example: "She works for a multinational corporation."
  },
  {
    word: "correct",
    phonetic: "/kəˈrekt/",
    definition: "right or true",
    example: "Your answer is correct."
  },
  {
    word: "correction",
    phonetic: "/kəˈrekʃən/",
    definition: "the act of making something right",
    example: "Please make the corrections to the document."
  },
  {
    word: "correspond",
    phonetic: "/ˌkɒrəˈspɒnd/",
    definition: "to write letters to someone",
    example: "They corresponded for many years before meeting in person."
  },
  {
    word: "correspondent",
    phonetic: "/ˌkɒrəˈspɒndənt/",
    definition: "a journalist who reports news from a particular country or area",
    example: "The newspaper's foreign correspondent reported from the war zone."
  },
  {
    word: "correspondence",
    phonetic: "/ˌkɒrəˈspɒndəns/",
    definition: "letters that are written or received",
    example: "I found an old correspondence between my grandparents."
  },
  {
    word: "corridor",
    phonetic: "/ˈkɒrɪdɔː/",
    definition: "a long passage in a building with rooms on either side",
    example: "The hotel rooms are along the corridor."
  },
  {
    word: "corrupt",
    phonetic: "/kəˈrʌpt/",
    definition: "dishonest or immoral",
    example: "The corrupt official was arrested for accepting bribes."
  },
  {
    word: "corruption",
    phonetic: "/kəˈrʌpʃən/",
    definition: "dishonest or immoral behavior",
    example: "The government is fighting corruption."
  },
  {
    word: "cosmic",
    phonetic: "/ˈkɒzmɪk/",
    definition: "relating to the universe",
    example: "Scientists are studying cosmic rays from outer space."
  },
  {
    word: "cosmetic",
    phonetic: "/kɒzˈmetɪk/",
    definition: "relating to beauty products",
    example: "She works for a cosmetic company."
  },
  {
    word: "cosmos",
    phonetic: "/ˈkɒzmɒs/",
    definition: "the universe considered as a system",
    example: "The stars in the cosmos are billions of light years away."
  },
  {
    word: "cost",
    phonetic: "/kɒst/",
    definition: "the amount of money that you need to buy or do something",
    example: "The cost of living has increased significantly."
  },
  {
    word: "costly",
    phonetic: "/ˈkɒstli/",
    definition: "expensive",
    example: "The car was too costly for me to buy."
  },
  {
    word: "cottage",
    phonetic: "/ˈkɒtɪdʒ/",
    definition: "a small house in the country",
    example: "They spent their vacation in a cozy cottage by the lake."
  },
  {
    word: "cotton",
    phonetic: "/ˈkɒtn/",
    definition: "a soft white material used for making clothes",
    example: "This shirt is made of cotton."
  },
  {
    word: "cough",
    phonetic: "/kɒf/",
    definition: "to force air out of your throat with a short, loud sound",
    example: "She has a bad cough and needs to see a doctor."
  },
  {
    word: "could",
    phonetic: "/kʊd/",
    definition: "used to say that something is possible",
    example: "Could you help me with this?"
  },
  {
    word: "council",
    phonetic: "/ˈkaʊnsl/",
    definition: "a group of people who are elected to make decisions",
    example: "The city council approved the new budget."
  },
  {
    word: "counsel",
    phonetic: "/ˈkaʊnsl/",
    definition: "advice given to someone about what they should do",
    example: "He sought legal counsel before signing the contract."
  },
  {
    word: "count",
    phonetic: "/kaʊnt/",
    definition: "to say numbers in order",
    example: "Can you count from 1 to 100?"
  },
  {
    word: "counter",
    phonetic: "/ˈkaʊntə/",
    definition: "a long flat surface in a shop, bank, etc., where people are served",
    example: "The customer stood at the counter waiting to be served."
  },
  {
    word: "country",
    phonetic: "/ˈkʌntri/",
    definition: "a nation with its own government",
    example: "France is a beautiful country."
  },
  {
    word: "countryside",
    phonetic: "/ˈkʌntrisaɪd/",
    definition: "land that is outside cities and towns",
    example: "We went for a walk in the countryside."
  },
  {
    word: "county",
    phonetic: "/ˈkaʊnti/",
    definition: "a large area of land that is part of a country or state",
    example: "She lives in a small town in the county of Kent."
  },
  {
    word: "couple",
    phonetic: "/ˈkʌpl/",
    definition: "two people who are married or in a romantic relationship",
    example: "The couple has been married for 50 years."
  },
  {
    word: "courage",
    phonetic: "/ˈkʌrɪdʒ/",
    definition: "the ability to do something that frightens you",
    example: "It took a lot of courage to speak in front of the large audience."
  },
  {
    word: "course",
    phonetic: "/kɔːs/",
    definition: "a series of lessons or lectures on a particular subject",
    example: "She's taking a course in computer programming."
  },
  {
    word: "court",
    phonetic: "/kɔːt/",
    definition: "a place where legal cases are heard",
    example: "The trial will take place in the criminal court."
  },
  {
    word: "courtesy",
    phonetic: "/ˈkɜːtəsi/",
    definition: "polite behavior",
    example: "He showed great courtesy to his guests."
  },
  {
    word: "cousin",
    phonetic: "/ˈkʌzn/",
    definition: "the child of your aunt or uncle",
    example: "My cousin is coming to visit next week."
  },
  {
    word: "cover",
    phonetic: "/ˈkʌvə/",
    definition: "to put something over or on top of something else",
    example: "Please cover the food with plastic wrap."
  },
  {
    word: "cow",
    phonetic: "/kaʊ/",
    definition: "a large female animal that is kept on farms for its milk",
    example: "The farmer milks the cows every morning."
  },
  {
    word: "coward",
    phonetic: "/ˈkaʊəd/",
    definition: "a person who is not brave",
    example: "He was called a coward for running away from the fight."
  },
  {
    word: "crab",
    phonetic: "/kræb/",
    definition: "a sea creature with a hard shell, eight legs, and two claws",
    example: "We ate crab for dinner."
  },
  {
    word: "crack",
    phonetic: "/kræk/",
    definition: "a narrow opening in something",
    example: "There's a crack in the wall."
  },
  {
    word: "craft",
    phonetic: "/krɑːft/",
    definition: "an activity involving making things with your hands",
    example: "She enjoys doing craft projects in her free time."
  },
  {
    word: "crayon",
    phonetic: "/ˈkreɪən/",
    definition: "a stick of colored wax used for drawing",
    example: "The children were drawing with crayons."
  },
  {
    word: "crazy",
    phonetic: "/ˈkreɪzi/",
    definition: "mentally ill",
    example: "He went crazy after the accident."
  },
  {
    word: "cream",
    phonetic: "/kriːm/",
    definition: "a thick liquid that is produced from milk",
    example: "She put cream in her coffee."
  },
  {
    word: "create",
    phonetic: "/kriːˈeɪt/",
    definition: "to make something new",
    example: "The artist created a beautiful painting."
  },
  {
    word: "creative",
    phonetic: "/kriːˈeɪtɪv/",
    definition: "able to produce new and original ideas",
    example: "She has a creative approach to problem-solving."
  },
  {
    word: "creature",
    phonetic: "/ˈkriːtʃə/",
    definition: "a living thing, especially an animal",
    example: "Dinosaurs were large creatures that lived millions of years ago."
  },
  {
    word: "credit",
    phonetic: "/ˈkredɪt/",
    definition: "an arrangement to pay for something at a later time",
    example: "She bought the car on credit."
  },
  {
    word: "creep",
    phonetic: "/kriːp/",
    definition: "to move slowly and quietly",
    example: "The cat crept up on the mouse."
  },
  {
    word: "crew",
    phonetic: "/kruː/",
    definition: "the people who work on a ship, plane, or train",
    example: "The crew of the ship worked hard to keep it running smoothly."
  },
  {
    word: "cricket",
    phonetic: "/ˈkrɪkɪt/",
    definition: "an insect that makes a chirping sound",
    example: "We could hear crickets chirping in the grass."
  },
  {
    word: "crime",
    phonetic: "/kraɪm/",
    definition: "an illegal act",
    example: "Murder is a serious crime."
  },
  {
    word: "criminal",
    phonetic: "/ˈkrɪmɪnl/",
    definition: "a person who has committed a crime",
    example: "The police are searching for the criminal."
  },
  {
    word: "crisis",
    phonetic: "/ˈkraɪsɪs/",
    definition: "a time of great danger or difficulty",
    example: "The country is facing an economic crisis."
  },
  {
    word: "crisp",
    phonetic: "/krɪsp/",
    definition: "hard but easily broken",
    example: "The apple was crisp and juicy."
  },
  {
    word: "criterion",
    phonetic: "/kraɪˈtɪəriən/",
    definition: "a standard by which something is judged",
    example: "The main criterion for the job is experience."
  },
  {
    word: "critic",
    phonetic: "/ˈkrɪtɪk/",
    definition: "a person who writes reviews of books, films, etc.",
    example: "The film received mixed reviews from critics."
  },
  {
    word: "critical",
    phonetic: "/ˈkrɪtɪkl/",
    definition: "expressing disapproval",
    example: "She was critical of his decision."
  },
  {
    word: "criticism",
    phonetic: "/ˈkrɪtɪsɪzəm/",
    definition: "the act of expressing disapproval",
    example: "He couldn't handle the criticism of his work."
  },
  {
    word: "criticize",
    phonetic: "/ˈkrɪtɪsaɪz/",
    definition: "to express disapproval of someone or something",
    example: "She criticized him for being late."
  },
  {
    word: "crop",
    phonetic: "/krɒp/",
    definition: "a plant that is grown in large quantities",
    example: "The farmers are harvesting their crops."
  },
  {
    word: "cross",
    phonetic: "/krɒs/",
    definition: "to go from one side of something to the other",
    example: "Be careful when crossing the street."
  },
  {
    word: "crossing",
    phonetic: "/ˈkrɒsɪŋ/",
    definition: "a place where people can cross a road, river, etc.",
    example: "There's a pedestrian crossing at the end of the street."
  },
  {
    word: "crossroad",
    phonetic: "/ˈkrɒsrəʊd/",
    definition: "a place where two roads meet",
    example: "Turn left at the crossroad."
  },
  {
    word: "crow",
    phonetic: "/krəʊ/",
    definition: "a large black bird",
    example: "Crows are often seen in urban areas."
  },
  {
    word: "crowd",
    phonetic: "/kraʊd/",
    definition: "a large group of people",
    example: "A crowd gathered to watch the parade."
  },
  {
    word: "crown",
    phonetic: "/kraʊn/",
    definition: "a circular decoration worn on the head of a king or queen",
    example: "The crown was made of gold and precious stones."
  },
  {
    word: "crucial",
    phonetic: "/ˈkruːʃl/",
    definition: "extremely important",
    example: "It is crucial that we arrive on time."
  },
  {
    word: "crude",
    phonetic: "/kruːd/",
    definition: "simple and not well made",
    example: "The shelter was made of crude materials."
  },
  {
    word: "cruel",
    phonetic: "/kruːəl/",
    definition: "causing pain or suffering to others",
    example: "It's cruel to treat animals badly."
  },
  {
    word: "cruelty",
    phonetic: "/ˈkruːəlti/",
    definition: "the act of causing pain or suffering to others",
    example: "The cruelty of the dictator was well known."
  },
  {
    word: "crush",
    phonetic: "/krʌʃ/",
    definition: "to press something so hard that it breaks or is damaged",
    example: "She crushed the can with her foot."
  },
  {
    word: "crust",
    phonetic: "/krʌst/",
    definition: "the hard outer layer of bread or pizza",
    example: "I like the crust of the bread."
  },
  {
    word: "cry",
    phonetic: "/kraɪ/",
    definition: "to produce tears from your eyes because you are sad or hurt",
    example: "The child cried when he fell down."
  },
  {
    word: "crystal",
    phonetic: "/ˈkrɪstl/",
    definition: "a clear, hard substance that is formed naturally",
    example: "The chandelier was made of crystal."
  },
  {
    word: "cube",
    phonetic: "/kjuːb/",
    definition: "a solid shape with six square sides",
    example: "Ice cubes are used to cool drinks."
  },
  {
    word: "cubic",
    phonetic: "/ˈkjuːbɪk/",
    definition: "relating to a cube",
    example: "The box has a volume of 100 cubic centimeters."
  },
  {
    word: "cucumber",
    phonetic: "/ˈkjuːkʌmbə/",
    definition: "a long green vegetable that is eaten raw",
    example: "She added cucumber to the salad."
  },
  {
    word: "cue",
    phonetic: "/kjuː/",
    definition: "a signal for someone to do something",
    example: "The director gave the cue to start filming."
  },
  {
    word: "cuff",
    phonetic: "/kʌf/",
    definition: "the end of a sleeve",
    example: "He rolled up his sleeves to the cuffs."
  },
  {
    word: "cultivate",
    phonetic: "/ˈkʌltɪveɪt/",
    definition: "to prepare land and grow crops on it",
    example: "The farmers cultivate corn and wheat."
  },
  {
    word: "culture",
    phonetic: "/ˈkʌltʃə/",
    definition: "the customs and beliefs of a particular group of people",
    example: "We need to respect different cultures."
  },
  {
    word: "cunning",
    phonetic: "/ˈkʌnɪŋ/",
    definition: "clever in a way that is not honest",
    example: "The fox is known for its cunning."
  },
  {
    word: "cup",
    phonetic: "/kʌp/",
    definition: "a small container used for drinking",
    example: "She poured coffee into the cup."
  },
  {
    word: "cupboard",
    phonetic: "/ˈkʌbəd/",
    definition: "a piece of furniture with doors and shelves for storing things",
    example: "The plates are in the cupboard."
  },
  {
    word: "cure",
    phonetic: "/kjʊə/",
    definition: "to make someone who is sick become well",
    example: "The medicine cured his headache."
  },
  {
    word: "curiosity",
    phonetic: "/ˌkjʊəriˈɒsəti/",
    definition: "the desire to know about something",
    example: "Children have a natural curiosity about the world."
  },
  {
    word: "curious",
    phonetic: "/ˈkjʊəriəs/",
    definition: "wanting to know about something",
    example: "I'm curious about what happened."
  },
  {
    word: "curl",
    phonetic: "/kɜːl/",
    definition: "to form into a curved shape",
    example: "Her hair curls naturally."
  },
  {
    word: "curriculum",
    phonetic: "/kəˈrɪkjʊləm/",
    definition: "the subjects that are taught in a school, college, etc.",
    example: "The school has a new curriculum for mathematics."
  },
  {
    word: "currency",
    phonetic: "/ˈkʌrənsi/",
    definition: "the money that is used in a particular country",
    example: "The local currency is the euro."
  },
  {
    word: "current",
    phonetic: "/ˈkʌrənt/",
    definition: "happening now",
    example: "The current situation is difficult."
  },
  {
    word: "curriculum",
    phonetic: "/kəˈrɪkjʊləm/",
    definition: "the subjects that are taught in a school, college, etc.",
    example: "The school has a new curriculum for mathematics."
  },
  {
    word: "curse",
    phonetic: "/kɜːs/",
    definition: "to use words that are intended to bring bad luck to someone",
    example: "She cursed the driver who cut her off."
  },
  {
    word: "curtain",
    phonetic: "/ˈkɜːtn/",
    definition: "a piece of cloth that hangs in front of a window or door",
    example: "She drew the curtains to block out the sunlight."
  },
  {
    word: "curve",
    phonetic: "/kɜːv/",
    definition: "a line that is not straight",
    example: "The road has many curves."
  },
  {
    word: "cushion",
    phonetic: "/ˈkʊʃən/",
    definition: "a soft object that you sit or lie on",
    example: "The sofa has several cushions."
  },
  {
    word: "custom",
    phonetic: "/ˈkʌstəm/",
    definition: "a traditional way of behaving",
    example: "It's a custom to exchange gifts at Christmas."
  },
  {
    word: "customer",
    phonetic: "/ˈkʌstəmə/",
    definition: "a person who buys goods or services",
    example: "The shop assistant helped the customer find what she was looking for."
  },
  {
    word: "customs",
    phonetic: "/ˈkʌstəmz/",
    definition: "the place where people are checked when they enter a country",
    example: "We had to go through customs at the airport."
  },
  {
    word: "cut",
    phonetic: "/kʌt/",
    definition: "to make an opening in something with a sharp tool",
    example: "She cut the cake into slices."
  },
  {
    word: "cute",
    phonetic: "/kjuːt/",
    definition: "attractive in a pretty way",
    example: "The baby is very cute."
  },
  {
    word: "cycle",
    phonetic: "/ˈsaɪkl/",
    definition: "a bicycle",
    example: "She rides her cycle to work every day."
  },
  {
    word: "cylinder",
    phonetic: "/ˈsɪlɪndə/",
    definition: "a solid or hollow shape with circular ends and straight sides",
    example: "The engine has four cylinders."
  },
  {
    word: "cynical",
    phonetic: "/ˈsɪnɪkl/",
    definition: "believing that people are only interested in themselves",
    example: "He has a cynical view of politics."
  },
  {
    word: "daily",
    phonetic: "/ˈdeɪli/",
    definition: "happening or done every day",
    example: "She reads the daily newspaper every morning."
  },
  {
    word: "dairy",
    phonetic: "/ˈdeəri/",
    definition: "relating to milk or food made from milk",
    example: "I need to buy some dairy products like milk and cheese."
  },
  {
    word: "dam",
    phonetic: "/dæm/",
    definition: "a wall built across a river to stop the flow of water",
    example: "The new dam will provide electricity for the whole region."
  },
  {
    word: "damage",
    phonetic: "/ˈdæmɪdʒ/",
    definition: "to harm or break something",
    example: "The heavy rain damaged many houses in the small village."
  },
  {
    word: "damp",
    phonetic: "/dæmp/",
    definition: "slightly wet, often in a way that is unpleasant",
    example: "The basement is always damp during the rainy season."
  },
  {
    word: "dance",
    phonetic: "/dɑːns/",
    definition: "to move your body to the rhythm of music",
    example: "They danced all night at the party."
  },
  {
    word: "danger",
    phonetic: "/ˈdeɪndʒə/",
    definition: "the possibility of harm or death",
    example: "Children should be taught about the dangers of playing with fire."
  },
  {
    word: "dangerous",
    phonetic: "/ˈdeɪndʒərəs/",
    definition: "likely to cause harm or death",
    example: "It's dangerous to walk alone in this area at night."
  },
  {
    word: "dare",
    phonetic: "/deə/",
    definition: "to be brave enough to do something",
    example: "I dare you to jump into the cold water."
  },
  {
    word: "dark",
    phonetic: "/dɑːk/",
    definition: "with little or no light",
    example: "It gets dark early in winter."
  },
  {
    word: "data",
    phonetic: "/ˈdeɪtə/",
    definition: "facts or information used to make decisions or analyze something",
    example: "The researchers collected a lot of data for their study."
  },
  {
    word: "date",
    phonetic: "/deɪt/",
    definition: "a particular day, month, or year",
    example: "What's the date of your birthday?"
  },
  {
    word: "daughter",
    phonetic: "/ˈdɔːtə/",
    definition: "a female child of a parent",
    example: "His daughter is studying medicine at university."
  },
  {
    word: "dawn",
    phonetic: "/dɔːn/",
    definition: "the time of day when light first appears",
    example: "We woke up at dawn to watch the sunrise."
  },
  {
    word: "day",
    phonetic: "/deɪ/",
    definition: "the period of time between sunrise and sunset",
    example: "We worked all day in the garden."
  },
  {
    word: "daylight",
    phonetic: "/ˈdeɪlaɪt/",
    definition: "the natural light of the sun during the day",
    example: "The room is bright with daylight coming through the windows."
  },
  {
    word: "dead",
    phonetic: "/ded/",
    definition: "no longer alive",
    example: "The plant is dead because I forgot to water it."
  },
  {
    word: "deadly",
    phonetic: "/ˈdedli/",
    definition: "causing or likely to cause death",
    example: "The snake's bite can be deadly if not treated quickly."
  },
  {
    word: "deaf",
    phonetic: "/def/",
    definition: "unable to hear",
    example: "He became deaf after a serious illness."
  },
  {
    word: "deal",
    phonetic: "/diːl/",
    definition: "an agreement or arrangement between people",
    example: "They made a deal to share the profits equally."
  },
  {
    word: "dear",
    phonetic: "/dɪə/",
    definition: "loved or valued very much",
    example: "My dear friend, I've missed you so much."
  },
  {
    word: "death",
    phonetic: "/deθ/",
    definition: "the end of life",
    example: "The death of her grandmother was very sad for the family."
  },
  {
    word: "debate",
    phonetic: "/dɪˈbeɪt/",
    definition: "a discussion where people express different opinions",
    example: "There was a heated debate about the new policy."
  },
  {
    word: "debt",
    phonetic: "/det/",
    definition: "money that you owe to someone",
    example: "He's trying to pay off his debts as quickly as possible."
  },
  {
    word: "decade",
    phonetic: "/ˈdekeɪd/",
    definition: "a period of ten years",
    example: "Great changes have taken place in the past decade."
  },
  {
    word: "decay",
    phonetic: "/dɪˈkeɪ/",
    definition: "to become bad or be destroyed by natural processes",
    example: "The old wooden house is starting to decay."
  },
  {
    word: "deceive",
    phonetic: "/dɪˈsiːv/",
    definition: "to make someone believe something that is not true",
    example: "He deceived his friends by lying about his past."
  },
  {
    word: "December",
    phonetic: "/dɪˈsembə/",
    definition: "the twelfth month of the year",
    example: "Christmas is celebrated in December."
  },
  {
    word: "decent",
    phonetic: "/ˈdiːsənt/",
    definition: "socially acceptable or good",
    example: "He's a decent person who always helps others."
  },
  {
    word: "decide",
    phonetic: "/dɪˈsaɪd/",
    definition: "to make a choice or judgment about something",
    example: "She decided to study abroad for a year."
  },
  {
    word: "decision",
    phonetic: "/dɪˈsɪʒən/",
    definition: "a choice or judgment that you make after thinking",
    example: "It was a difficult decision to leave her job."
  },
  {
    word: "deck",
    phonetic: "/dek/",
    definition: "a flat surface on a ship or boat",
    example: "The passengers were standing on the deck watching the sunset."
  },
  {
    word: "declare",
    phonetic: "/dɪˈkleə/",
    definition: "to say something officially or publicly",
    example: "The government declared a state of emergency."
  },
  {
    word: "decorate",
    phonetic: "/ˈdekəreɪt/",
    definition: "to make something look more attractive by adding things",
    example: "They decorated the room with balloons and streamers for the party."
  },
  {
    word: "decrease",
    phonetic: "/dɪˈkriːs/",
    definition: "to become less in size, amount, or number",
    example: "The number of students in the class has decreased."
  },
  {
    word: "dedicate",
    phonetic: "/ˈdedɪkeɪt/",
    definition: "to give all your attention and effort to something",
    example: "She dedicated her life to helping poor children."
  },
  {
    word: "deed",
    phonetic: "/diːd/",
    definition: "something that someone does, especially something good",
    example: "Helping the elderly is a good deed."
  },
  {
    word: "deep",
    phonetic: "/diːp/",
    definition: "going a long way down from the top or surface",
    example: "The water in the lake is very deep."
  },
  {
    word: "deer",
    phonetic: "/dɪə/",
    definition: "a wild animal with four legs that eats grass and leaves",
    example: "We saw a deer in the forest."
  },
  {
    word: "defeat",
    phonetic: "/dɪˈfiːt/",
    definition: "to win against someone in a fight, war, or competition",
    example: "Our team was defeated in the final match."
  },
  {
    word: "defect",
    phonetic: "/ˈdiːfekt/",
    definition: "a fault or problem in something",
    example: "The car was returned to the factory because of a defect."
  },
  {
    word: "defence",
    phonetic: "/dɪˈfens/",
    definition: "the act of protecting someone or something from attack",
    example: "The country has a strong defence system."
  },
  {
    word: "defend",
    phonetic: "/dɪˈfend/",
    definition: "to protect someone or something from attack",
    example: "The soldiers defended the town against the enemy."
  },
  {
    word: "define",
    phonetic: "/dɪˈfaɪn/",
    definition: "to explain the meaning of a word or concept",
    example: "The dictionary defines 'happiness' as the state of being happy."
  },
  {
    word: "definite",
    phonetic: "/ˈdefɪnɪt/",
    definition: "clear and certain",
    example: "We need a definite answer by tomorrow."
  },
  {
    word: "definitely",
    phonetic: "/ˈdefɪnɪtli/",
    definition: "without any doubt",
    example: "I will definitely come to your party."
  },
  {
    word: "definition",
    phonetic: "/ˌdefɪˈnɪʃən/",
    definition: "a statement that explains the meaning of a word or concept",
    example: "Can you give me the definition of this technical term?"
  },
  {
    word: "degree",
    phonetic: "/dɪˈɡriː/",
    definition: "a unit for measuring temperature or angles",
    example: "Water boils at 100 degrees Celsius."
  },
  {
    word: "delay",
    phonetic: "/dɪˈleɪ/",
    definition: "to make someone or something late",
    example: "The flight was delayed due to bad weather."
  },
  {
    word: "delete",
    phonetic: "/dɪˈliːt/",
    definition: "to remove something, especially from a computer",
    example: "I accidentally deleted all my photos."
  },
  {
    word: "delegation",
    phonetic: "/ˌdelɪˈɡeɪʃən/",
    definition: "a group of people who represent a larger group",
    example: "A delegation from our company will attend the conference."
  },
  {
    word: "delicate",
    phonetic: "/ˈdelɪkət/",
    definition: "easily broken or damaged",
    example: "Be careful with that vase - it's very delicate."
  },
  {
    word: "delicious",
    phonetic: "/dɪˈlɪʃəs/",
    definition: "tasting very good",
    example: "The food at that restaurant is delicious."
  },
  {
    word: "delight",
    phonetic: "/dɪˈlaɪt/",
    definition: "great pleasure or happiness",
    example: "The children screamed with delight when they saw the presents."
  },
  {
    word: "deliver",
    phonetic: "/dɪˈlɪvə/",
    definition: "to take goods, letters, etc. to a particular place or person",
    example: "The company promises to deliver the goods within three working days."
  },
  {
    word: "delivery",
    phonetic: "/dɪˈlɪvəri/",
    definition: "the act of taking goods, letters, etc. to a place or person",
    example: "The delivery of the new furniture will be next week."
  },
  {
    word: "demand",
    phonetic: "/dɪˈmɑːnd/",
    definition: "to ask for something in a forceful way",
    example: "The workers are demanding higher wages."
  },
  {
    word: "democracy",
    phonetic: "/dɪˈmɒkrəsi/",
    definition: "a system of government where people vote to choose their leaders",
    example: "Many countries around the world practice democracy."
  },
  {
    word: "democratic",
    phonetic: "/ˌdeməˈkrætɪk/",
    definition: "based on the principles of democracy",
    example: "They want a more democratic society."
  },
  {
    word: "demonstrate",
    phonetic: "/ˈdemənstreɪt/",
    definition: "to show or prove something clearly",
    example: "The experiment demonstrates how gravity works."
  },
  {
    word: "dense",
    phonetic: "/dens/",
    definition: "closely packed together",
    example: "The forest has a dense growth of trees."
  },
  {
    word: "density",
    phonetic: "/ˈdensəti/",
    definition: "the degree to which something is dense",
    example: "The population density in this city is very high."
  },
  {
    word: "deny",
    phonetic: "/dɪˈnaɪ/",
    definition: "to say that something is not true",
    example: "He denied stealing the money."
  },
  {
    word: "depart",
    phonetic: "/dɪˈpɑːt/",
    definition: "to leave a place, especially to start a journey",
    example: "The train departs at 10:30."
  },
  {
    word: "department",
    phonetic: "/dɪˈpɑːtmənt/",
    definition: "a part of an organization that deals with a particular area of work",
    example: "She works in the sales department."
  },
  {
    word: "departure",
    phonetic: "/dɪˈpɑːtʃə/",
    definition: "the act of leaving a place",
    example: "His departure was delayed because of the bad weather."
  },
  {
    word: "depend",
    phonetic: "/dɪˈpend/",
    definition: "to trust someone or something and know that he, she, or it will help you or do what you want or expect",
    example: "Whether we can go hiking tomorrow depends on the weather."
  },
  {
    word: "dependent",
    phonetic: "/dɪˈpendənt/",
    definition: "needing someone or something for help or support",
    example: "Children are dependent on their parents for food and shelter."
  },
  {
    word: "deposit",
    phonetic: "/dɪˈpɒzɪt/",
    definition: "to put money into a bank account",
    example: "She deposits her salary into the bank every month."
  },
  {
    word: "depress",
    phonetic: "/dɪˈpres/",
    definition: "to make someone feel sad",
    example: "The bad news depressed everyone."
  },
  {
    word: "depth",
    phonetic: "/depθ/",
    definition: "the distance from the top or surface to the bottom of something",
    example: "The depth of the swimming pool is 2 meters."
  },
  {
    word: "derive",
    phonetic: "/dɪˈraɪv/",
    definition: "to get something from a particular source",
    example: "The word 'computer' derives from the Latin word 'computare'."
  },
  {
    word: "descend",
    phonetic: "/dɪˈsend/",
    definition: "to go down from a higher place to a lower place",
    example: "The plane began to descend towards the airport."
  },
  {
    word: "describe",
    phonetic: "/dɪˈskraɪb/",
    definition: "to say what someone or something is like",
    example: "Can you describe the man who stole your bag?"
  },
  {
    word: "description",
    phonetic: "/dɪˈskrɪpʃən/",
    definition: "a piece of writing or speech that says what someone or something is like",
    example: "The job advertisement gives a detailed description of the duties."
  },
  {
    word: "deserve",
    phonetic: "/dɪˈzɜːv/",
    definition: "to have earned something because of your actions or qualities",
    example: "She deserves to be promoted for her hard work."
  },
  {
    word: "design",
    phonetic: "/dɪˈzaɪn/",
    definition: "to plan and make something for a specific purpose",
    example: "He designed a new type of engine for the car."
  },
  {
    word: "desirable",
    phonetic: "/dɪˈzaɪərəbl/",
    definition: "worth having or wanting",
    example: "A good education is desirable for everyone."
  },
  {
    word: "desire",
    phonetic: "/dɪˈzaɪə/",
    definition: "a strong feeling of wanting something",
    example: "She has a strong desire to become a doctor."
  },
  {
    word: "desk",
    phonetic: "/desk/",
    definition: "a piece of furniture with a flat top where you can work, write, etc.",
    example: "There's a computer on his desk."
  },
  {
    word: "despair",
    phonetic: "/dɪˈspeə/",
    definition: "the feeling that there is no hope",
    example: "He felt despair when he lost his job."
  },
  {
    word: "despise",
    phonetic: "/dɪˈspaɪz/",
    definition: "to hate someone or something very much",
    example: "She despises people who are cruel to animals."
  },
  {
    word: "despite",
    phonetic: "/dɪˈspaɪt/",
    definition: "in spite of",
    example: "Despite the rain, we still went for a walk."
  },
  {
    word: "destroy",
    phonetic: "/dɪˈstrɔɪ/",
    definition: "to damage something so badly that it cannot be repaired",
    example: "The fire destroyed the entire building."
  },
  {
    word: "destruction",
    phonetic: "/dɪˈstrʌkʃən/",
    definition: "the act of destroying something",
    example: "The destruction caused by the earthquake was enormous."
  },
  {
    word: "detail",
    phonetic: "/ˈdiːteɪl/",
    definition: "a small part or piece of information about something",
    example: "He explained the plan in great detail."
  },
  {
    word: "detect",
    phonetic: "/dɪˈtekt/",
    definition: "to notice or discover something that is not easy to see",
    example: "The doctor detected a problem with her heart."
  },
  {
    word: "determination",
    phonetic: "/dɪˌtɜːmɪˈneɪʃən/",
    definition: "the quality of being determined to do something",
    example: "Her determination to succeed helped her overcome many difficulties."
  },
  {
    word: "determine",
    phonetic: "/dɪˈtɜːmɪn/",
    definition: "to decide something officially or with authority",
    example: "The court will determine the outcome of the case."
  },
  {
    word: "develop",
    phonetic: "/dɪˈveləp/",
    definition: "to grow or change into a more advanced or stronger form",
    example: "The company is developing a new product for the market."
  },
  {
    word: "development",
    phonetic: "/dɪˈveləpmənt/",
    definition: "the process of growing or changing",
    example: "The development of technology has changed our lives greatly."
  },
  {
    word: "device",
    phonetic: "/dɪˈvaɪs/",
    definition: "a machine or tool that does a special job",
    example: "This device helps people with hearing problems."
  },
  {
    word: "devise",
    phonetic: "/dɪˈvaɪz/",
    definition: "to invent or plan something",
    example: "They devised a plan to escape from the prison."
  },
  {
    word: "devote",
    phonetic: "/dɪˈvəʊt/",
    definition: "to give all your time and attention to something",
    example: "She devotes all her free time to volunteering."
  },
  {
    word: "dew",
    phonetic: "/djuː/",
    definition: "small drops of water that form on surfaces during the night",
    example: "The grass was covered with dew in the early morning."
  },
  {
    word: "dialog",
    phonetic: "/ˈdaɪəlɒɡ/",
    definition: "a conversation between two or more people",
    example: "The book contains a lot of dialog between the characters."
  },
  {
    word: "diameter",
    phonetic: "/daɪˈæmɪtə/",
    definition: "a straight line passing through the center of a circle",
    example: "The diameter of the circle is 10 centimeters."
  },
  {
    word: "diamond",
    phonetic: "/ˈdaɪəmənd/",
    definition: "a very hard, clear precious stone",
    example: "She wears a ring with a diamond on her finger."
  },
  {
    word: "diary",
    phonetic: "/ˈdaɪəri/",
    definition: "a book where you write down your thoughts and experiences",
    example: "She keeps a diary every day."
  },
  {
    word: "dictate",
    phonetic: "/dɪkˈteɪt/",
    definition: "to speak words for someone else to write down",
    example: "The manager dictated a letter to his secretary."
  },
  {
    word: "dictionary",
    phonetic: "/ˈdɪkʃənəri/",
    definition: "a book that contains words and their meanings",
    example: "I need to look up this word in the dictionary."
  },
  {
    word: "die",
    phonetic: "/daɪ/",
    definition: "to stop living",
    example: "The old tree died after the long drought."
  },
  {
    word: "diet",
    phonetic: "/ˈdaɪət/",
    definition: "the food that a person or animal usually eats",
    example: "She's on a diet to lose weight."
  },
  {
    word: "differ",
    phonetic: "/ˈdɪfə/",
    definition: "to be different from something or someone",
    example: "The two paintings differ in style and color."
  },
  {
    word: "difference",
    phonetic: "/ˈdɪfrəns/",
    definition: "the way in which two or more things are not the same",
    example: "What's the difference between these two products?"
  },
  {
    word: "different",
    phonetic: "/ˈdɪfrənt/",
    definition: "not the same as something or someone else",
    example: "This book is different from the one I read last week."
  },
  {
    word: "difficult",
    phonetic: "/ˈdɪfɪkəlt/",
    definition: "not easy to do or understand",
    example: "The exam was very difficult."
  },
  {
    word: "difficulty",
    phonetic: "/ˈdɪfɪkəlti/",
    definition: "a problem or something that is hard to do",
    example: "We had difficulty finding the way to the hotel."
  },
  {
    word: "dig",
    phonetic: "/dɪɡ/",
    definition: "to make a hole in the ground using a tool or your hands",
    example: "The children are digging in the garden."
  },
  {
    word: "digest",
    phonetic: "/daɪˈdʒest/",
    definition: "to process food in the stomach so that it can be used by the body",
    example: "It takes about 24 hours for food to be digested."
  },
  {
    word: "digital",
    phonetic: "/ˈdɪdʒɪtl/",
    definition: "using or relating to computer technology",
    example: "Most cameras today are digital."
  },
  {
    word: "dim",
    phonetic: "/dɪm/",
    definition: "not bright or clear",
    example: "The light in the room is very dim."
  },
  {
    word: "dimension",
    phonetic: "/daɪˈmenʃən/",
    definition: "a measurement of length, width, or height",
    example: "The dimensions of the room are 4 meters by 5 meters."
  },
  {
    word: "dinner",
    phonetic: "/ˈdɪnə/",
    definition: "the main meal of the day, usually eaten in the evening",
    example: "We're having chicken for dinner tonight."
  },
  {
    word: "dip",
    phonetic: "/dɪp/",
    definition: "to put something into a liquid and then take it out quickly",
    example: "She dipped her finger into the sauce to taste it."
  },
  {
    word: "diplomatic",
    phonetic: "/ˌdɪpləˈmætɪk/",
    definition: "relating to the profession or skill of managing international relations",
    example: "He has a diplomatic passport that allows him to travel easily."
  },
  {
    word: "direct",
    phonetic: "/dəˈrekt/",
    definition: "going straight to a place without turning or stopping",
    example: "The direct flight from Beijing to New York takes about 13 hours."
  },
    {
    word: "direction",
    phonetic: "/dəˈrekʃən/",
    definition: "the way that you should go to get to a place",
    example: "Can you give me directions to the nearest hospital?"
  },
  {
    word: "directly",
    phonetic: "/dəˈrektli/",
    definition: "immediately or without delay",
    example: "I'll call you directly after the meeting."
  },
  {
    word: "director",
    phonetic: "/dəˈrektə/",
    definition: "a person who is in charge of a company or organization",
    example: "The director of the company made an important announcement today."
  },
  {
    word: "dirt",
    phonetic: "/dɜːt/",
    definition: "dust, soil, or mud",
    example: "His shoes were covered in dirt after playing in the garden."
  },
  {
    word: "dirty",
    phonetic: "/ˈdɜːti/",
    definition: "not clean",
    example: "The children came home with dirty clothes after playing outside."
  },
  {
    word: "disappear",
    phonetic: "/ˌdɪsəˈpɪə/",
    definition: "to become impossible to see",
    example: "The sun disappeared behind the clouds."
  },
  {
    word: "disappoint",
    phonetic: "/ˌdɪsəˈpɔɪnt/",
    definition: "to make someone feel sad because something did not happen as expected",
    example: "I'm sorry to disappoint you, but I can't come to the party."
  },
  {
    word: "disaster",
    phonetic: "/dɪˈzɑːstə/",
    definition: "a very bad event that causes a lot of damage or loss of life",
    example: "The earthquake was a terrible disaster that killed thousands of people."
  },
  {
    word: "disc",
    phonetic: "/dɪsk/",
    definition: "a flat, round object, especially a CD or DVD",
    example: "He bought a new disc for his computer."
  },
    {
    word: "discard",
    phonetic: "/dɪsˈkɑːd/",
    definition: "to throw something away because it is not useful or wanted",
    example: "She discarded the old newspapers in the recycling bin."
  },
  {
    word: "discharge",
    phonetic: "/dɪsˈtʃɑːdʒ/",
    definition: "to allow someone to leave a hospital or a job",
    example: "The patient was discharged from the hospital yesterday."
  },
  {
    word: "discipline",
    phonetic: "/ˈdɪsəplɪn/",
    definition: "the practice of training people to obey rules",
    example: "Good discipline is important in a classroom."
  },
  {
    word: "disclose",
    phonetic: "/dɪsˈkləʊz/",
    definition: "to make something known that was previously secret",
    example: "The company disclosed its financial results for the year."
  },
  {
    word: "discount",
    phonetic: "/ˈdɪskaʊnt/",
    definition: "a reduction in the usual price of something",
    example: "The store is offering a 20% discount on all shoes."
  },
  {
    word: "discourage",
    phonetic: "/dɪsˈkʌrɪdʒ/",
    definition: "to make someone less confident or less willing to do something",
    example: "Don't let failures discourage you from trying again."
  },
  {
    word: "discover",
    phonetic: "/dɪsˈkʌvə/",
    definition: "to find something that was not known before",
    example: "Scientists discovered a new species of plant in the rainforest."
  },
  {
    word: "discovery",
    phonetic: "/dɪsˈkʌvəri/",
    definition: "the act of finding something that was not known before",
    example: "The discovery of penicillin was a major breakthrough in medicine."
  },
  {
    word: "discuss",
    phonetic: "/dɪsˈkʌs/",
    definition: "to talk about something with other people",
    example: "We need to discuss the problem and find a solution."
  },
  {
    word: "discussion",
    phonetic: "/dɪsˈkʌʃən/",
    definition: "a conversation about a particular subject",
    example: "There was a lively discussion about the new policy."
  },
  {
    word: "disease",
    phonetic: "/dɪˈziːz/",
    definition: "an illness that affects people, animals, or plants",
    example: "The doctor is researching a cure for the disease."
  },
  {
    word: "disgust",
    phonetic: "/dɪsˈɡʌst/",
    definition: "a strong feeling of dislike or disapproval",
    example: "The smell of the garbage filled her with disgust."
  },
  {
    word: "dish",
    phonetic: "/dɪʃ/",
    definition: "a container for food, or the food served in it",
    example: "She prepared a delicious dish for dinner."
  },
  {
    word: "dislike",
    phonetic: "/dɪsˈlaɪk/",
    definition: "to not like someone or something",
    example: "I dislike getting up early in the morning."
  },
  {
    word: "dismiss",
    phonetic: "/dɪsˈmɪs/",
    definition: "to tell someone to leave, or to remove someone from a job",
    example: "The manager dismissed the employee for being late too often."
  },
  {
    word: "disorder",
    phonetic: "/dɪsˈɔːdə/",
    definition: "a state of confusion or lack of organization",
    example: "The room was in complete disorder after the party."
  },
  {
    word: "display",
    phonetic: "/dɪˈspleɪ/",
    definition: "to show something for people to see",
    example: "The museum is displaying works by Picasso this month."
  },
  {
    word: "dispose",
    phonetic: "/dɪˈspəʊz/",
    definition: "to get rid of something",
    example: "We need to dispose of this old furniture."
  },
  {
    word: "dispute",
    phonetic: "/dɪˈspjuːt/",
    definition: "an argument or disagreement",
    example: "They had a dispute over who should pay the bill."
  },
  {
    word: "dissolve",
    phonetic: "/dɪˈzɒlv/",
    definition: "to mix with a liquid and become part of it",
    example: "Sugar dissolves in water."
  },
  {
    word: "distance",
    phonetic: "/ˈdɪstəns/",
    definition: "the amount of space between two places or things",
    example: "The distance between Beijing and Shanghai is about 1,300 kilometers."
  },
  {
    word: "distant",
    phonetic: "/ˈdɪstənt/",
    definition: "far away in space or time",
    example: "The stars are distant from the Earth."
  },
  {
    word: "distinct",
    phonetic: "/dɪˈstɪŋkt/",
    definition: "clearly different or separate",
    example: "There's a distinct difference between the two products."
  },
  {
    word: "distinction",
    phonetic: "/dɪˈstɪŋkʃən/",
    definition: "a difference between similar things",
    example: "He made a distinction between right and wrong."
  },
  {
    word: "distinguish",
    phonetic: "/dɪˈstɪŋɡwɪʃ/",
    definition: "to recognize the difference between things",
    example: "It's hard to distinguish between the two twin brothers."
  },
  {
    word: "distress",
    phonetic: "/dɪˈstres/",
    definition: "great pain, sadness, or suffering",
    example: "The news caused great distress to the family."
  },
  {
    word: "distribute",
    phonetic: "/dɪˈstrɪbjuːt/",
    definition: "to give or send things to a lot of people",
    example: "The organization distributes food to homeless people."
  },
  {
    word: "district",
    phonetic: "/ˈdɪstrɪkt/",
    definition: "an area of a country or city",
    example: "She lives in the business district of the city."
  },
  {
    word: "disturb",
    phonetic: "/dɪˈstɜːb/",
    definition: "to interrupt someone or something",
    example: "Please don't disturb me while I'm working."
  },
  {
    word: "ditch",
    phonetic: "/dɪtʃ/",
    definition: "a long narrow hole in the ground that carries water",
    example: "The farmers dug ditches to irrigate their fields."
  },
  {
    word: "dive",
    phonetic: "/daɪv/",
    definition: "to jump into water with your head first",
    example: "The children love to dive into the swimming pool."
  },
  {
    word: "diverse",
    phonetic: "/daɪˈvɜːs/",
    definition: "very different from each other",
    example: "The city has a diverse population with people from many countries."
  },
  {
    word: "divide",
    phonetic: "/dɪˈvaɪd/",
    definition: "to separate something into parts",
    example: "The teacher divided the class into groups of four."
  },
  {
    word: "division",
    phonetic: "/dɪˈvɪʒən/",
    definition: "the act of dividing something into parts",
    example: "The division of the company into smaller units improved efficiency."
  },
  {
    word: "divorce",
    phonetic: "/dɪˈvɔːs/",
    definition: "the legal ending of a marriage",
    example: "They got divorced after being married for 10 years."
  },
  {
    word: "dizzy",
    phonetic: "/ˈdɪzi/",
    definition: "feeling as if everything is spinning around you",
    example: "The ride on the roller coaster made her feel dizzy."
  },
  {
    word: "do",
    phonetic: "/duː/",
    definition: "to perform an action",
    example: "What do you do for a living?"
  },
  {
    word: "doctor",
    phonetic: "/ˈdɒktə/",
    definition: "a person who is trained to treat sick people",
    example: "She went to see the doctor because she had a fever."
  },
  {
    word: "document",
    phonetic: "/ˈdɒkjʊmənt/",
    definition: "a piece of paper with information written on it",
    example: "Please sign this document to confirm your agreement."
  },
  {
    word: "dog",
    phonetic: "/dɒɡ/",
    definition: "a domestic animal with four legs and a tail",
    example: "My dog loves to play fetch in the park."
  },
  {
    word: "doll",
    phonetic: "/dɒl/",
    definition: "a toy that looks like a small person",
    example: "The little girl is playing with her doll."
  },
  {
    word: "dollar",
    phonetic: "/ˈdɒlə/",
    definition: "the main unit of money in the US, Canada, etc.",
    example: "The book costs 20 dollars."
  },
  {
    word: "domain",
    phonetic: "/dəˈmeɪn/",
    definition: "an area of knowledge or activity",
    example: "This subject is outside my domain of expertise."
  },
  {
    word: "dome",
    phonetic: "/dəʊm/",
    definition: "a round roof on a building",
    example: "The cathedral has a beautiful dome."
  },
  {
    word: "domestic",
    phonetic: "/dəˈmestɪk/",
    definition: "relating to the home or family",
    example: "She does all the domestic chores like cooking and cleaning."
  },
  {
    word: "dominant",
    phonetic: "/ˈdɒmɪnənt/",
    definition: "more important, powerful, or noticeable than other things",
    example: "The dominant color in the painting is blue."
  },
  {
    word: "dominate",
    phonetic: "/ˈdɒmɪneɪt/",
    definition: "to have control over someone or something",
    example: "The company dominates the market for computer software."
  },
  {
    word: "donate",
    phonetic: "/dəʊˈneɪt/",
    definition: "to give money or goods to a charity or organization",
    example: "She donates 10% of her income to charity every year."
  },
  {
    word: "donkey",
    phonetic: "/ˈdɒŋki/",
    definition: "an animal like a small horse with long ears",
    example: "The farmer uses a donkey to carry heavy loads."
  },
  {
    word: "door",
    phonetic: "/dɔː/",
    definition: "a flat object that opens and closes to allow entrance to a building or room",
    example: "Please close the door when you leave."
  },
  {
    word: "dormitory",
    phonetic: "/ˈdɔːmɪtəri/",
    definition: "a building where students live at a school or university",
    example: "She shares a room with three other students in the dormitory."
  },
  {
    word: "dose",
    phonetic: "/dəʊs/",
    definition: "an amount of medicine that you take at one time",
    example: "The doctor prescribed a dose of antibiotics."
  },
  {
    word: "dot",
    phonetic: "/dɒt/",
    definition: "a small round mark",
    example: "There's a red dot on the map to show where the museum is."
  },
  {
    word: "double",
    phonetic: "/ˈdʌbl/",
    definition: "twice the size, amount, or number of something",
    example: "The company's profits doubled last year."
  },
  {
    word: "doubt",
    phonetic: "/daʊt/",
    definition: "a feeling of uncertainty about something",
    example: "I have some doubt about his ability to do the job."
  },
  {
    word: "doubtful",
    phonetic: "/ˈdaʊtfəl/",
    definition: "not certain or likely",
    example: "It's doubtful that we'll finish the project on time."
  },
  {
    word: "down",
    phonetic: "/daʊn/",
    definition: "towards or in a lower place or position",
    example: "She fell down and hurt her knee."
  },
  {
    word: "downstairs",
    phonetic: "/ˌdaʊnˈsteəz/",
    definition: "on or to the ground floor of a building",
    example: "The kitchen is downstairs."
  },
  {
    word: "downtown",
    phonetic: "/ˌdaʊnˈtaʊn/",
    definition: "the main business area of a city",
    example: "There are many shops and restaurants downtown."
  },
  {
    word: "dozen",
    phonetic: "/ˈdʌzn/",
    definition: "twelve of something",
    example: "She bought a dozen eggs at the supermarket."
  },
  {
    word: "draft",
    phonetic: "/drɑːft/",
    definition: "a preliminary version of a document",
    example: "He's working on the first draft of his novel."
  },
  {
    word: "drag",
    phonetic: "/dræɡ/",
    definition: "to pull something along the ground",
    example: "The children dragged the heavy box across the floor."
  },
  {
    word: "dragon",
    phonetic: "/ˈdræɡən/",
    definition: "a large imaginary animal that breathes fire",
    example: "The knight fought the dragon to save the princess."
  },
  {
    word: "drain",
    phonetic: "/dreɪn/",
    definition: "to remove liquid from something",
    example: "The water drained out of the sink."
  },
  {
    word: "drama",
    phonetic: "/ˈdrɑːmə/",
    definition: "a play for the theater, television, or radio",
    example: "She's studying drama at university."
  },
  {
    word: "dramatic",
    phonetic: "/drəˈmætɪk/",
    definition: "very exciting or impressive",
    example: "There was a dramatic change in the weather yesterday."
  },
  {
    word: "draw",
    phonetic: "/drɔː/",
    definition: "to make a picture using a pencil, pen, etc.",
    example: "She loves to draw pictures of animals."
  },
  {
    word: "drawer",
    phonetic: "/drɔː/",
    definition: "a box-shaped container that slides in and out of a piece of furniture",
    example: "She keeps her socks in the top drawer of the dresser."
  },
  {
    word: "drawing",
    phonetic: "/ˈdrɔːɪŋ/",
    definition: "a picture made with a pencil, pen, etc.",
    example: "He showed me his drawing of a castle."
  },
  {
    word: "dream",
    phonetic: "/driːm/",
    definition: "a series of images that you see in your mind while you are asleep",
    example: "I had a strange dream last night."
  },
  {
    word: "dress",
    phonetic: "/dres/",
    definition: "a piece of clothing worn by women or girls that covers the body from the shoulders to the legs",
    example: "She wore a beautiful dress to the party."
  },
  {
    word: "drift",
    phonetic: "/drɪft/",
    definition: "to move slowly in a particular direction",
    example: "The boat drifted out to sea."
  },
  {
    word: "drill",
    phonetic: "/drɪl/",
    definition: "a tool used for making holes",
    example: "He used a drill to make a hole in the wall."
  },
  {
    word: "drink",
    phonetic: "/drɪŋk/",
    definition: "to take liquid into your mouth and swallow it",
    example: "She drinks coffee every morning."
  },
  {
    word: "drip",
    phonetic: "/drɪp/",
    definition: "to fall in small drops",
    example: "The faucet is dripping water."
  },
  {
    word: "drive",
    phonetic: "/draɪv/",
    definition: "to operate a car or other vehicle",
    example: "She drives to work every day."
  },
  {
    word: "driver",
    phonetic: "/ˈdraɪvə/",
    definition: "a person who drives a car or other vehicle",
    example: "The driver of the bus was very friendly."
  },
  {
    word: "drop",
    phonetic: "/drɒp/",
    definition: "to let something fall",
    example: "She dropped the glass and it broke."
  },
  {
    word: "drought",
    phonetic: "/draʊt/",
    definition: "a long period of time without rain",
    example: "The drought caused many crops to fail."
  },
  {
    word: "drown",
    phonetic: "/draʊn/",
    definition: "to die because you cannot breathe under water",
    example: "He almost drowned when he fell into the river."
  },
  {
    word: "drug",
    phonetic: "/drʌɡ/",
    definition: "a medicine or substance that affects the body",
    example: "The doctor prescribed some drugs for his headache."
  },
  {
    word: "drum",
    phonetic: "/drʌm/",
    definition: "a musical instrument that you hit with sticks or your hands",
    example: "He plays the drums in a rock band."
  },
  {
    word: "drunk",
    phonetic: "/drʌŋk/",
    definition: "affected by alcohol so that you cannot think or behave normally",
    example: "He was so drunk that he couldn't walk straight."
  },
  {
    word: "dry",
    phonetic: "/draɪ/",
    definition: "not wet or containing water",
    example: "The clothes are dry after being in the sun."
  },
  {
    word: "duck",
    phonetic: "/dʌk/",
    definition: "a water bird with a flat beak",
    example: "There are many ducks swimming in the pond."
  },
  {
    word: "due",
    phonetic: "/djuː/",
    definition: "expected to happen or arrive at a particular time",
    example: "The train is due to arrive at 3:30."
  },
  {
    word: "dull",
    phonetic: "/dʌl/",
    definition: "not interesting or exciting",
    example: "The lecture was so dull that many students fell asleep."
  },
  {
    word: "dumb",
    phonetic: "/dʌm/",
    definition: "unable to speak",
    example: "The shock left her temporarily dumb."
  },
  {
    word: "dump",
    phonetic: "/dʌmp/",
    definition: "to put something down in a careless way",
    example: "He dumped his backpack on the floor."
  },
  {
    word: "durable",
    phonetic: "/ˈdjʊərəbl/",
    definition: "able to last for a long time without breaking or being damaged",
    example: "These shoes are very durable and should last for years."
  },
  {
    word: "duration",
    phonetic: "/djuˈreɪʃən/",
    definition: "the length of time that something continues",
    example: "The duration of the concert was two hours."
  },
  {
    word: "during",
    phonetic: "/ˈdjʊərɪŋ/",
    definition: "throughout the course or period of",
    example: "We had a great time during our vacation."
  },
  {
    word: "dusk",
    phonetic: "/dʌsk/",
    definition: "the time just before night when it is not completely dark",
    example: "The sky turns beautiful colors at dusk."
  },
  {
    word: "dust",
    phonetic: "/dʌst/",
    definition: "tiny particles of dirt or sand in the air or on surfaces",
    example: "She wiped the dust off the table with a cloth."
  },
  {
    word: "duty",
    phonetic: "/ˈdjuːti/",
    definition: "something that you have to do because it is your responsibility",
    example: "It's my duty to help those in need."
  },
  {
    word: "dwarf",
    phonetic: "/dwɔːf/",
    definition: "a person or animal that is much smaller than normal",
    example: "The story is about a dwarf who lives in a forest."
  },
  {
    word: "dwell",
    phonetic: "/dwel/",
    definition: "to live in a particular place",
    example: "The family has dwelled in this house for generations."
  },
  {
    word: "dwelling",
    phonetic: "/ˈdwelɪŋ/",
    definition: "a place where someone lives",
    example: "The city has built new dwellings for low-income families."
  },
  {
    word: "dye",
    phonetic: "/daɪ/",
    definition: "a substance used to change the color of something",
    example: "She used red dye to color her hair."
  },
  {
    word: "dynamic",
    phonetic: "/daɪˈnæmɪk/",
    definition: "full of energy and enthusiasm",
    example: "He has a dynamic personality that makes him popular."
  },
  {
    word: "dynasty",
    phonetic: "/ˈdɪnəsti/",
    definition: "a series of rulers from the same family",
    example: "The Ming Dynasty ruled China from 1368 to 1644."
  },
  {
    word: "each",
    phonetic: "/iːtʃ/",
    definition: "every one of two or more people or things considered separately",
    example: "Each student must complete the assignment by Friday."
  },
  {
    word: "eager",
    phonetic: "/ˈiːɡə/",
    definition: "wanting very much to do or have something",
    example: "She was eager to start her new job."
  },
  {
    word: "eagle",
    phonetic: "/ˈiːɡl/",
    definition: "a large bird with a hooked beak that hunts and eats small animals",
    example: "We saw an eagle flying high in the sky."
  },
  {
    word: "ear",
    phonetic: "/ɪə/",
    definition: "the organ of hearing and balance in humans and other vertebrates",
    example: "He has a good ear for music."
  },
  {
    word: "early",
    phonetic: "/ˈɜːli/",
    definition: "happening or done before the usual or expected time",
    example: "She gets up early every morning to go for a run."
  },
  {
    word: "earn",
    phonetic: "/ɜːn/",
    definition: "to receive money for work that you do",
    example: "He earns a good salary as a software engineer."
  },
  {
    word: "earnest",
    phonetic: "/ˈɜːnɪst/",
    definition: "serious and determined",
    example: "She made an earnest effort to improve her grades."
  },
  {
    word: "earth",
    phonetic: "/ɜːθ/",
    definition: "the planet on which we live; the world",
    example: "Scientists are studying the effects of pollution on Earth."
  },
  {
    word: "earthquake",
    phonetic: "/ˈɜːθkweɪk/",
    definition: "a sudden violent movement of the earth's surface",
    example: "The earthquake caused widespread damage to buildings."
  },
  {
    word: "ease",
    phonetic: "/iːz/",
    definition: "the state of being comfortable or free from pain",
    example: "He settled into the chair with a sigh of ease."
  },
  {
    word: "east",
    phonetic: "/iːst/",
    definition: "the direction from which the sun rises",
    example: "The city is located to the east of the mountains."
  },
  {
    word: "eastern",
    phonetic: "/ˈiːstən/",
    definition: "relating to or situated in the east",
    example: "Eastern countries have different cultural traditions."
  },
  {
    word: "easy",
    phonetic: "/ˈiːzi/",
    definition: "not difficult; done or obtained without great effort",
    example: "This is an easy recipe to follow."
  },
  {
    word: "eat",
    phonetic: "/iːt/",
    definition: "to put food into the mouth, chew it, and swallow it",
    example: "We usually eat dinner at 7 o'clock."
  },
  {
    word: "echo",
    phonetic: "/ˈekəʊ/",
    definition: "a sound that is heard again after it has been reflected off a surface",
    example: "The echo of our voices could be heard in the cave."
  },
  {
    word: "economic",
    phonetic: "/ˌiːkəˈnɒmɪk/",
    definition: "relating to the economy of a country or region",
    example: "The government is implementing new economic policies."
  },
  {
    word: "economical",
    phonetic: "/ˌiːkəˈnɒmɪkl/",
    definition: "using money, time, goods, etc. carefully and not wastefully",
    example: "She's very economical with her money."
  },
  {
    word: "economy",
    phonetic: "/ɪˈkɒnəmi/",
    definition: "the system by which a country's money, industry, and trade are organized",
    example: "The economy is growing at a steady rate."
  },
  {
    word: "edge",
    phonetic: "/edʒ/",
    definition: "the thin sharp part of a blade or tool",
    example: "Be careful with the edge of the knife."
  },
  {
    word: "edit",
    phonetic: "/ˈedɪt/",
    definition: "to prepare a text or film for publication by correcting and improving it",
    example: "She spent hours editing her essay before submitting it."
  },
  {
    word: "edition",
    phonetic: "/ɪˈdɪʃən/",
    definition: "a particular version of a book, newspaper, or magazine",
    example: "The latest edition of the dictionary includes many new words."
  },
  {
    word: "editor",
    phonetic: "/ˈedɪtə/",
    definition: "a person who prepares text for publication",
    example: "The editor suggested some changes to improve the article."
  },
  {
    word: "educate",
    phonetic: "/ˈedʒukeɪt/",
    definition: "to teach someone, especially in a school or college",
    example: "The school aims to educate children to be responsible citizens."
  },
  {
    word: "education",
    phonetic: "/ˌedʒuˈkeɪʃən/",
    definition: "the process of teaching or learning in a school or college",
    example: "A good education is essential for success in life."
  },
  {
    word: "effect",
    phonetic: "/ɪˈfekt/",
    definition: "a change that results from an action or cause",
    example: "The medicine had no effect on his condition."
  },
  {
    word: "effective",
    phonetic: "/ɪˈfektɪv/",
    definition: "producing the desired result",
    example: "The new policy has been very effective in reducing pollution."
  },
  {
    word: "efficiency",
    phonetic: "/ɪˈfɪʃənsi/",
    definition: "the quality of doing something well with no waste of time or money",
    example: "The company is trying to improve efficiency in the workplace."
  },
  {
    word: "efficient",
    phonetic: "/ɪˈfɪʃənt/",
    definition: "working well and without waste",
    example: "She is an efficient worker who always meets deadlines."
  },
  {
    word: "effort",
    phonetic: "/ˈefət/",
    definition: "physical or mental energy that is needed to do something",
    example: "He made a great effort to finish the project on time."
  },
  {
    word: "egg",
    phonetic: "/eɡ/",
    definition: "an oval object produced by a female bird, from which a young bird hatches",
    example: "She boiled three eggs for breakfast."
  },
  {
    word: "eight",
    phonetic: "/eɪt/",
    definition: "the number 8",
    example: "There are eight planets in our solar system."
  },
  {
    word: "eighteen",
    phonetic: "/ˌeɪˈtiːn/",
    definition: "the number 18",
    example: "She started college when she was eighteen."
  },
  {
    word: "eighth",
    phonetic: "/eɪtθ/",
    definition: "one of eight equal parts of something",
    example: "He ate an eighth of the cake."
  },
  {
    word: "eighty",
    phonetic: "/ˈeɪti/",
    definition: "the number 80",
    example: "She celebrated her eightieth birthday last week."
  },
    {
    word: "either",
    phonetic: "/ˈaɪðə/",
    definition: "one or the other of two people or things",
    example: "You can choose either the red shirt or the blue one."
  },
  {
    word: "elaborate",
    phonetic: "/ɪˈlæbərət/",
    definition: "detailed and complicated in design or planning",
    example: "She gave an elaborate explanation of how the machine works."
  },
  {
    word: "elastic",
    phonetic: "/ɪˈlæstɪk/",
    definition: "able to stretch and then return to its original shape",
    example: "The waistband of these pants is elastic."
  },
  {
    word: "elbow",
    phonetic: "/ˈelbəʊ/",
    definition: "the joint between the upper and lower parts of the arm",
    example: "He leaned on the table with his elbow."
  },
  {
    word: "elder",
    phonetic: "/ˈeldə/",
    definition: "older than someone else",
    example: "Her elder brother is studying medicine."
  },
  {
    word: "elect",
    phonetic: "/ɪˈlekt/",
    definition: "to choose someone for a position by voting",
    example: "They elected her as president of the club."
  },
  {
    word: "election",
    phonetic: "/ɪˈlekʃən/",
    definition: "the process of choosing someone for a position by voting",
    example: "The national election will be held next month."
  },
  {
    word: "electric",
    phonetic: "/ɪˈlektrɪk/",
    definition: "using or producing electricity",
    example: "We need to buy a new electric kettle."
  },
  {
    word: "electrical",
    phonetic: "/ɪˈlektrɪkl/",
    definition: "relating to electricity",
    example: "He's an electrical engineer who designs circuits."
  },
  {
    word: "electricity",
    phonetic: "/ɪˌlekˈtrɪsəti/",
    definition: "a form of energy used for heating, lighting, and powering machines",
    example: "The electricity went out during the storm."
  },
  {
    word: "electron",
    phonetic: "/ɪˈlektrɒn/",
    definition: "a tiny particle with a negative charge that moves around the nucleus of an atom",
    example: "Electrons are fundamental particles in atoms."
  },
  {
    word: "electronic",
    phonetic: "/ɪˌlekˈtrɒnɪk/",
    definition: "using or operated by devices that use transistors and microchips",
    example: "She bought a new electronic dictionary."
  },
  {
    word: "electronics",
    phonetic: "/ɪˌlekˈtrɒnɪks/",
    definition: "the branch of physics that deals with the behavior of electrons",
    example: "He's studying electronics at university."
  },
  {
    word: "element",
    phonetic: "/ˈelɪmənt/",
    definition: "a basic part of something",
    example: "Trust is an important element in any relationship."
  },
  {
    word: "elementary",
    phonetic: "/ˌelɪˈmentəri/",
    definition: "basic or simple",
    example: "The book explains elementary principles of mathematics."
  },
  {
    word: "elephant",
    phonetic: "/ˈelɪfənt/",
    definition: "a very large animal with a long trunk and tusks",
    example: "We saw several elephants at the zoo."
  },
  {
    word: "elevator",
    phonetic: "/ˈelɪveɪtə/",
    definition: "a machine that carries people or goods up and down in a building",
    example: "Take the elevator to the fifth floor."
  },
  {
    word: "eleven",
    phonetic: "/ɪˈlevn/",
    definition: "the number 11",
    example: "There are eleven players on a soccer team."
  },
  {
    word: "eliminate",
    phonetic: "/ɪˈlɪmɪneɪt/",
    definition: "to remove or get rid of something",
    example: "The company is trying to eliminate waste in production."
  },
  {
    word: "else",
    phonetic: "/els/",
    definition: "in addition to what has been mentioned",
    example: "Do you want anything else from the store?"
  },
  {
    word: "elsewhere",
    phonetic: "/ˌelsˈweə/",
    definition: "in or to another place",
    example: "If you can't find it here, try looking elsewhere."
  },
  {
    word: "embarrass",
    phonetic: "/ɪmˈbærəs/",
    definition: "to make someone feel ashamed or uncomfortable",
    example: "He was embarrassed by his mistake."
  },
  {
    word: "embrace",
    phonetic: "/ɪmˈbreɪs/",
    definition: "to put your arms around someone as a sign of love or friendship",
    example: "They embraced each other warmly."
  },
  {
    word: "emerge",
    phonetic: "/ɪˈmɜːdʒ/",
    definition: "to come out of a place or to appear from somewhere",
    example: "The sun emerged from behind the clouds."
  },
  {
    word: "emergency",
    phonetic: "/ɪˈmɜːdʒənsi/",
    definition: "a serious situation that needs immediate action",
    example: "Call 911 in case of emergency."
  },
  {
    word: "emit",
    phonetic: "/ɪˈmɪt/",
    definition: "to produce and give out something such as light, heat, or sound",
    example: "The sun emits light and heat."
  },
  {
    word: "emotion",
    phonetic: "/ɪˈməʊʃən/",
    definition: "a strong feeling such as love, anger, or fear",
    example: "She couldn't hide her emotions when she heard the news."
  },
  {
    word: "emotional",
    phonetic: "/ɪˈməʊʃənl/",
    definition: "relating to emotions",
    example: "It was an emotional moment when they met again after many years."
  },
  {
    word: "emphasis",
    phonetic: "/ˈemfəsɪs/",
    definition: "special importance or attention given to something",
    example: "The teacher put emphasis on the importance of reading."
  },
  {
    word: "emphasize",
    phonetic: "/ˈemfəsaɪz/",
    definition: "to give special importance or attention to something",
    example: "The report emphasizes the need for better education."
  },
  {
    word: "empire",
    phonetic: "/ˈempaɪə/",
    definition: "a group of countries ruled by a single person or government",
    example: "The Roman Empire was one of the largest in history."
  },
  {
    word: "employ",
    phonetic: "/ɪmˈplɔɪ/",
    definition: "to pay someone to work for you",
    example: "The company employs over 500 people."
  },
  {
    word: "employee",
    phonetic: "/ɪmˈplɔɪiː/",
    definition: "a person who is paid to work for a company or organization",
    example: "All employees must attend the meeting."
  },
  {
    word: "employer",
    phonetic: "/ɪmˈplɔɪə/",
    definition: "a person or company that pays people to work for them",
    example: "The employer provides health insurance for all workers."
  },
  {
    word: "employment",
    phonetic: "/ɪmˈplɔɪmənt/",
    definition: "the state of having a paid job",
    example: "The government is trying to increase employment opportunities."
  },
  {
    word: "empty",
    phonetic: "/ˈempti/",
    definition: "containing nothing; not filled or occupied",
    example: "The room was empty when we arrived."
  },
  {
    word: "enable",
    phonetic: "/ɪˈneɪbl/",
    definition: "to make it possible for someone to do something",
    example: "The new technology enables us to communicate more easily."
  },
  {
    word: "enclose",
    phonetic: "/ɪnˈkləʊz/",
    definition: "to surround or close off an area",
    example: "The garden is enclosed by a high wall."
  },
  {
    word: "encounter",
    phonetic: "/ɪnˈkaʊntə/",
    definition: "to meet someone or something, especially unexpectedly",
    example: "We encountered a lot of traffic on the way."
  },
  {
    word: "encourage",
    phonetic: "/ɪnˈkʌrɪdʒ/",
    definition: "to give someone support or confidence",
    example: "Her teacher encouraged her to study harder."
  },
  {
    word: "end",
    phonetic: "/end/",
    definition: "the part of something that is furthest from the start",
    example: "He lives at the end of the street."
  },
  {
    word: "ending",
    phonetic: "/ˈendɪŋ/",
    definition: "the final part of a story, movie, or event",
    example: "The movie has a happy ending."
  },
  {
    word: "endless",
    phonetic: "/ˈendləs/",
    definition: "having no end or limit",
    example: "It seemed like an endless journey."
  },
  {
    word: "endure",
    phonetic: "/ɪnˈdjʊə/",
    definition: "to suffer something difficult or painful patiently",
    example: "She endured years of hardship before becoming successful."
  },
  {
    word: "enemy",
    phonetic: "/ˈenəmi/",
    definition: "a person who hates or opposes another",
    example: "They were bitter enemies for many years."
  },
  {
    word: "energy",
    phonetic: "/ˈenədʒi/",
    definition: "the ability to do work or be active",
    example: "He has a lot of energy despite his age."
  },
  {
    word: "enforce",
    phonetic: "/ɪnˈfɔːs/",
    definition: "to make people obey a law or rule",
    example: "The police are responsible for enforcing the law."
  },
  {
    word: "engage",
    phonetic: "/ɪnˈɡeɪdʒ/",
    definition: "to be involved in an activity",
    example: "She's engaged in research on cancer treatment."
  },
  {
    word: "engine",
    phonetic: "/ˈendʒɪn/",
    definition: "a machine that converts energy into motion",
    example: "The car's engine is very powerful."
  },
  {
    word: "engineer",
    phonetic: "/ˌendʒɪˈnɪə/",
    definition: "a person who designs or builds machines, structures, or systems",
    example: "He works as a software engineer."
  },
  {
    word: "engineering",
    phonetic: "/ˌendʒɪˈnɪərɪŋ/",
    definition: "the branch of science and technology concerned with the design and building of machines and structures",
    example: "She's studying civil engineering at university."
  },
  {
    word: "enhance",
    phonetic: "/ɪnˈhɑːns/",
    definition: "to improve the quality, amount, or strength of something",
    example: "Regular exercise can enhance your physical strength and mental health."
  },
  {
    word: "enjoy",
    phonetic: "/ɪnˈdʒɔɪ/",
    definition: "to get pleasure from something",
    example: "I enjoy reading books in my free time."
  },
  {
    word: "enlarge",
    phonetic: "/ɪnˈlɑːdʒ/",
    definition: "to make something bigger",
    example: "The company plans to enlarge its factory."
  },
  {
    word: "enlighten",
    phonetic: "/ɪnˈlaɪtn/",
    definition: "to give someone information or understanding",
    example: "The book enlightened me about the history of the region."
  },
  {
    word: "enormous",
    phonetic: "/ɪˈnɔːməs/",
    definition: "very large in size or amount",
    example: "They built an enormous house in the countryside."
  },
  {
    word: "enough",
    phonetic: "/ɪˈnʌf/",
    definition: "as much or as many as needed",
    example: "We have enough food for everyone."
  },
  {
    word: "enquire",
    phonetic: "/ɪnˈkwaɪə/",
    definition: "to ask for information",
    example: "I'll enquire about the availability of tickets."
  },
  {
    word: "enrich",
    phonetic: "/ɪnˈrɪtʃ/",
    definition: "to improve the quality or value of something",
    example: "Travel enriches our understanding of different cultures."
  },
  {
    word: "enroll",
    phonetic: "/ɪnˈrəʊl/",
    definition: "to officially register as a student or member of an organization",
    example: "She enrolled in a cooking class."
  },
  {
    word: "ensure",
    phonetic: "/ɪnˈʃʊə/",
    definition: "to make certain that something happens",
    example: "We need to ensure that all safety regulations are followed."
  },
  {
    word: "enter",
    phonetic: "/ˈentə/",
    definition: "to come or go into a place",
    example: "Please enter the building through the main entrance."
  },
  {
    word: "enterprise",
    phonetic: "/ˈentəpraɪz/",
    definition: "a business or company",
    example: "The family runs a successful manufacturing enterprise."
  },
  {
    word: "entertain",
    phonetic: "/ˌentəˈteɪn/",
    definition: "to amuse or interest people",
    example: "The clown entertained the children with funny tricks."
  },
  {
    word: "entertainment",
    phonetic: "/ˌentəˈteɪnmənt/",
    definition: "activities that amuse or interest people",
    example: "The city offers a wide range of entertainment options."
  },
  {
    word: "enthusiasm",
    phonetic: "/ɪnˈθjuːziæzəm/",
    definition: "great interest or excitement about something",
    example: "He has a lot of enthusiasm for his work."
  },
  {
    word: "enthusiastic",
    phonetic: "/ɪnˌθjuːziˈæstɪk/",
    definition: "showing great interest or excitement",
    example: "The students gave an enthusiastic response to the new teacher."
  },
  {
    word: "entire",
    phonetic: "/ɪnˈtaɪə/",
    definition: "complete; whole",
    example: "She spent the entire day cleaning the house."
  },
  {
    word: "entrance",
    phonetic: "/ˈentrəns/",
    definition: "a way into a building or place",
    example: "The main entrance is on the north side of the building."
  },
  {
    word: "entry",
    phonetic: "/ˈentri/",
    definition: "the act of entering a place or joining an organization",
    example: "His entry into the competition was unexpected."
  },
  {
    word: "envelope",
    phonetic: "/ˈenvələʊp/",
    definition: "a flat paper container for a letter",
    example: "She put the letter in an envelope and sealed it."
  },
  {
    word: "environment",
    phonetic: "/ɪnˈvaɪrənmənt/",
    definition: "the natural world in which people, animals, and plants live",
    example: "We need to protect the environment for future generations."
  },
  {
    word: "envy",
    phonetic: "/ˈenvi/",
    definition: "the feeling of wanting something that someone else has",
    example: "She felt envy when she saw her friend's new car."
  },
  {
    word: "equal",
    phonetic: "/ˈiːkwəl/",
    definition: "the same in size, amount, or value",
    example: "All people are equal before the law."
  },
  {
    word: "equality",
    phonetic: "/iːˈkwɒləti/",
    definition: "the state of being equal in rights, status, or opportunities",
    example: "The organization fights for gender equality."
  },
  {
    word: "equation",
    phonetic: "/ɪˈkweɪʒən/",
    definition: "a mathematical statement that two expressions are equal",
    example: "Solve the equation for x."
  },
  {
    word: "equip",
    phonetic: "/ɪˈkwɪp/",
    definition: "to provide someone or something with the things they need",
    example: "The school is equipped with modern facilities."
  },
  {
    word: "equipment",
    phonetic: "/ɪˈkwɪpmənt/",
    definition: "the tools or machines needed for a particular activity",
    example: "The laboratory has sophisticated equipment for research."
  },
  {
    word: "equivalent",
    phonetic: "/ɪˈkwɪvələnt/",
    definition: "equal in value, amount, or meaning",
    example: "One dollar is equivalent to about 7 yuan."
  },
  {
    word: "era",
    phonetic: "/ˈɪərə/",
    definition: "a period of time in history",
    example: "The computer has revolutionized our modern era."
  },
  {
    word: "erase",
    phonetic: "/ɪˈreɪz/",
    definition: "to remove something by rubbing it out or deleting it",
    example: "She erased the mistake with a rubber."
  },
  {
    word: "erect",
    phonetic: "/ɪˈrekt/",
    definition: "to build or put up a structure",
    example: "They erected a tent in the middle of the field."
  },
  {
    word: "error",
    phonetic: "/ˈerə/",
    definition: "a mistake",
    example: "There was an error in the calculation."
  },
  {
    word: "escape",
    phonetic: "/ɪˈskeɪp/",
    definition: "to get away from a place where you are trapped",
    example: "The prisoner escaped from jail."
  },
  {
    word: "especially",
    phonetic: "/ɪˈspeʃəli/",
    definition: "particularly; more than usual",
    example: "I enjoy all kinds of music, especially classical."
  },
  {
    word: "essay",
    phonetic: "/ˈeseɪ/",
    definition: "a short piece of writing on a particular subject",
    example: "She wrote an essay about environmental protection."
  },
  {
    word: "essence",
    phonetic: "/ˈesəns/",
    definition: "the basic or most important quality of something",
    example: "The essence of his argument is that we need to act now."
  },
  {
    word: "essential",
    phonetic: "/ɪˈsenʃl/",
    definition: "necessary; extremely important",
    example: "Water is essential for life."
  },
  {
    word: "establish",
    phonetic: "/ɪˈstæblɪʃ/",
    definition: "to start a company, organization, or system",
    example: "The university was established in 1905."
  },
  {
    word: "establishment",
    phonetic: "/ɪˈstæblɪʃmənt/",
    definition: "a business or organization",
    example: "The restaurant is a popular establishment in the city."
  },
  {
    word: "estate",
    phonetic: "/ɪˈsteɪt/",
    definition: "a large area of land with a big house on it",
    example: "The wealthy family owns a vast estate in the countryside."
  },
  {
    word: "esteem",
    phonetic: "/ɪˈstiːm/",
    definition: "respect and admiration for someone",
    example: "He is held in high esteem by his colleagues."
  },
  {
    word: "estimate",
    phonetic: "/ˈestɪmeɪt/",
    definition: "to calculate or judge the value, size, or cost of something",
    example: "The project will cost an estimated $10 million."
  },
  {
    word: "eternal",
    phonetic: "/ɪˈtɜːnl/",
    definition: "lasting forever",
    example: "Many people believe in eternal life after death."
  },
  {
    word: "Europe",
    phonetic: "/ˈjʊərəp/",
    definition: "the continent that is to the east of the Atlantic Ocean",
    example: "She's planning a trip to Europe next summer."
  },
  {
    word: "European",
    phonetic: "/ˌjʊərəˈpiːən/",
    definition: "relating to Europe or its people",
    example: "European countries have strong economic ties."
  },
  {
    word: "evaluate",
    phonetic: "/ɪˈvæljueɪt/",
    definition: "to judge the value or quality of something",
    example: "Teachers evaluate students' work regularly."
  },
  {
    word: "evaluation",
    phonetic: "/ɪˌvæljuˈeɪʃən/",
    definition: "the process of judging the value or quality of something",
    example: "The evaluation of the project will be completed next month."
  },
  {
    word: "evaporate",
    phonetic: "/ɪˈvæpəreɪt/",
    definition: "to change from a liquid to a gas",
    example: "The water in the puddle evaporated in the sun."
  },
  {
    word: "eve",
    phonetic: "/iːv/",
    definition: "the day or evening before an important day",
    example: "We're having a party on New Year's Eve."
  },
  {
    word: "even",
    phonetic: "/ˈiːvn/",
    definition: "flat and smooth with no parts that are higher than others",
    example: "The surface of the table is very even."
  },
  {
    word: "evening",
    phonetic: "/ˈiːvnɪŋ/",
    definition: "the part of the day between the afternoon and night",
    example: "We're having dinner together this evening."
  },
  {
    word: "event",
    phonetic: "/ɪˈvent/",
    definition: "something that happens, especially something important",
    example: "The wedding was a big event for the family."
  },
  {
    word: "eventually",
    phonetic: "/ɪˈventʃuəli/",
    definition: "finally; after a long time",
    example: "He worked hard and eventually succeeded."
  },
  {
    word: "ever",
    phonetic: "/ˈevə/",
    definition: "at any time",
    example: "Have you ever been to Paris?"
  },
  {
    word: "every",
    phonetic: "/ˈevri/",
    definition: "all of the people or things in a group",
    example: "Every student must pass the exam to graduate."
  },
  {
    word: "everybody",
    phonetic: "/ˈevribɒdi/",
    definition: "every person",
    example: "Everybody enjoyed the party."
  },
  {
    word: "everyday",
    phonetic: "/ˈevrideɪ/",
    definition: "happening or used every day",
    example: "These are my everyday clothes."
  },
  {
    word: "everyone",
    phonetic: "/ˈevriwʌn/",
    definition: "every person",
    example: "Everyone is welcome to attend the meeting."
  },
  {
    word: "everything",
    phonetic: "/ˈevriθɪŋ/",
    definition: "all things",
    example: "She knows everything about computers."
  },
  {
    word: "everywhere",
    phonetic: "/ˈevriweə/",
    definition: "in all places",
    example: "There are flowers everywhere in the garden."
  },
  {
    word: "evidence",
    phonetic: "/ˈevɪdəns/",
    definition: "facts or information that show something is true",
    example: "There is evidence that the Earth is getting warmer."
  },
  {
    word: "evident",
    phonetic: "/ˈevɪdənt/",
    definition: "clear or obvious",
    example: "It was evident that she was upset."
  },
  {
    word: "evil",
    phonetic: "/ˈiːvl/",
    definition: "morally wrong or bad",
    example: "Evil actions will eventually be punished."
  },
  {
    word: "evolve",
    phonetic: "/ɪˈvɒlv/",
    definition: "to develop gradually",
    example: "The company has evolved from a small business to a large corporation."
  },
  {
    word: "exact",
    phonetic: "/ɪɡˈzækt/",
    definition: "completely correct or accurate",
    example: "I need the exact time of the meeting."
  },
  {
    word: "exaggerate",
    phonetic: "/ɪɡˈzædʒəreɪt/",
    definition: "to make something seem larger, better, or worse than it really is",
    example: "He tends to exaggerate his achievements."
  },
  {
    word: "exam",
    phonetic: "/ɪɡˈzæm/",
    definition: "a test of knowledge or ability",
    example: "She's studying for her final exams."
  },
  {
    word: "examine",
    phonetic: "/ɪɡˈzæmɪn/",
    definition: "to look at something carefully in order to learn about it",
    example: "The doctor examined the patient thoroughly."
  },
  {
    word: "example",
    phonetic: "/ɪɡˈzɑːmpl/",
    definition: "something that shows what other things of the same kind are like",
    example: "This painting is a good example of her early work."
  },
  {
    word: "excellent",
    phonetic: "/ˈeksələnt/",
    definition: "extremely good",
    example: "The food at the restaurant was excellent."
  },
  {
    word: "except",
    phonetic: "/ɪkˈsept/",
    definition: "not including; apart from",
    example: "Everyone came to the party except John."
  },
  {
    word: "exception",
    phonetic: "/ɪkˈsepʃən/",
    definition: "someone or something that is not included in a general statement",
    example: "Most of the students passed the test, with only a few exceptions."
  },
  {
    word: "excess",
    phonetic: "/ɪkˈses/",
    definition: "an amount that is more than needed",
    example: "Avoid eating food that is high in fat and sugar."
  },
  {
    word: "excessive",
    phonetic: "/ɪkˈsesɪv/",
    definition: "too much; more than is reasonable or necessary",
    example: "The company was fined for excessive pollution."
  },
  {
    word: "exchange",
    phonetic: "/ɪksˈtʃeɪndʒ/",
    definition: "to give something to someone and receive something else in return",
    example: "We exchanged addresses before saying goodbye."
  },
  {
    word: "excite",
    phonetic: "/ɪkˈsaɪt/",
    definition: "to make someone feel enthusiastic or eager",
    example: "The news excited everyone in the office."
  },
  {
    word: "excitement",
    phonetic: "/ɪkˈsaɪtmənt/",
    definition: "the feeling of being excited",
    example: "There was great excitement before the concert."
  },
  {
    word: "exciting",
    phonetic: "/ɪkˈsaɪtɪŋ/",
    definition: "causing feelings of enthusiasm and eagerness",
    example: "It was an exciting adventure."
  },
  {
    word: "exclaim",
    phonetic: "/ɪkˈskleɪm/",
    definition: "to say something loudly and suddenly because of surprise or strong emotion",
    example: "She exclaimed in surprise when she saw the gift."
  },
  {
    word: "exclude",
    phonetic: "/ɪkˈskluːd/",
    definition: "to prevent someone or something from entering a place or taking part in an activity",
    example: "The club excludes people under 18."
  },
  {
    word: "exclusive",
    phonetic: "/ɪkˈskluːsɪv/",
    definition: "limited to a particular person or group",
    example: "The hotel offers exclusive services to its VIP guests."
  },
  {
    word: "excursion",
    phonetic: "/ɪkˈskɜːʃən/",
    definition: "a short journey or trip, especially for pleasure",
    example: "The school organized an excursion to the museum."
  },
  {
    word: "excuse",
    phonetic: "/ɪkˈskjuːz/",
    definition: "a reason given to explain why someone did something wrong",
    example: "He made up an excuse for being late."
  },
  {
    word: "execute",
    phonetic: "/ˈeksɪkjuːt/",
    definition: "to carry out a plan or order",
    example: "The team executed the project successfully."
  },
  {
    word: "executive",
    phonetic: "/ɪɡˈzekjətɪv/",
    definition: "a person in a high position in a company or organization",
    example: "The company's executives held a meeting to discuss the new strategy."
  },
  {
    word: "exercise",
    phonetic: "/ˈeksəsaɪz/",
    definition: "physical activity that you do to stay healthy",
    example: "Regular exercise is good for your health."
  },
  {
    word: "exert",
    phonetic: "/ɪɡˈzɜːt/",
    definition: "to use physical or mental energy to do something",
    example: "He exerted all his strength to lift the heavy box."
  },
  {
    word: "exhaust",
    phonetic: "/ɪɡˈzɔːst/",
    definition: "to make someone very tired",
    example: "The long journey exhausted us."
  },
  {
    word: "exhibit",
    phonetic: "/ɪɡˈzɪbɪt/",
    definition: "to show something publicly",
    example: "The museum is exhibiting works by Picasso."
  },
  {
    word: "exhibition",
    phonetic: "/ˌeksɪˈbɪʃən/",
    definition: "a public display of works of art or items of interest",
    example: "There's an exhibition of ancient artifacts at the museum."
  },
  {
    word: "exist",
    phonetic: "/ɪɡˈzɪst/",
    definition: "to be real or to be present in a place",
    example: "Dinosaurs no longer exist."
  },
  {
    word: "existence",
    phonetic: "/ɪɡˈzɪstəns/",
    definition: "the state of being real or present",
    example: "Scientists are studying the existence of life on other planets."
  },
  {
    word: "exit",
    phonetic: "/ˈeksɪt/",
    definition: "a way out of a building or room",
    example: "The emergency exit is at the back of the theater."
  },
  {
    word: "expand",
    phonetic: "/ɪkˈspænd/",
    definition: "to become larger in size, number, or amount",
    example: "The company plans to expand into new markets."
  },
  {
    word: "expansion",
    phonetic: "/ɪkˈspænʃən/",
    definition: "the process of becoming larger",
    example: "The expansion of the city has led to environmental problems."
  },
  {
    word: "expect",
    phonetic: "/ɪkˈspekt/",
    definition: "to think that something will happen",
    example: "I expect to receive the package tomorrow."
  },
  {
    word: "expectation",
    phonetic: "/ˌekspekˈteɪʃən/",
    definition: "the feeling that something good is going to happen",
    example: "He has high expectations for his children."
  },
  {
    word: "expense",
    phonetic: "/ɪkˈspens/",
    definition: "the cost of something",
    example: "The expense of living in this city is very high."
  },
  {
    word: "expensive",
    phonetic: "/ɪkˈspensɪv/",
    definition: "costing a lot of money",
    example: "She bought an expensive car with her savings."
  },
  {
    word: "experience",
    phonetic: "/ɪksˈpɪəriəns/",
    definition: "knowledge or skill that you gain from doing something",
    example: "He has many years of experience in teaching."
  },
  {
    word: "experiment",
    phonetic: "/ɪksˈperɪmənt/",
    definition: "a scientific test to discover what happens in particular conditions",
    example: "The scientists conducted an experiment to test their theory."
  },
  {
    word: "expert",
    phonetic: "/ˈekspɜːt/",
    definition: "a person who has special knowledge or skill in a particular area",
    example: "She's an expert in environmental science."
  },
  {
    word: "explain",
    phonetic: "/ɪksˈpleɪn/",
    definition: "to make something clear or easy to understand",
    example: "Can you explain how this machine works?"
  },
  {
    word: "explanation",
    phonetic: "/ˌekspləˈneɪʃən/",
    definition: "a statement that makes something clear",
    example: "She gave a detailed explanation of the problem."
  },
  {
    word: "explode",
    phonetic: "/ɪksˈpləʊd/",
    definition: "to burst with a loud noise",
    example: "The bomb exploded, causing extensive damage."
  },
  {
    word: "exploit",
    phonetic: "/ɪksˈplɔɪt/",
    definition: "to use something in a way that helps you",
    example: "Some companies exploit their workers by paying low wages."
  },
  {
    word: "explore",
    phonetic: "/ɪksˈplɔː/",
    definition: "to travel around an area to learn about it",
    example: "They explored the forest looking for rare plants."
  },
  {
    word: "explosion",
    phonetic: "/ɪksˈpləʊʒən/",
    definition: "a sudden and violent burst",
    example: "The explosion was heard several miles away."
  },
  {
    word: "explosive",
    phonetic: "/ɪksˈpləʊsɪv/",
    definition: "able to explode",
    example: "The factory stores explosive materials safely."
  },
  {
    word: "export",
    phonetic: "/ɪksˈpɔːt/",
    definition: "to send goods to another country for sale",
    example: "The country exports oil to many parts of the world."
  },
  {
    word: "expose",
    phonetic: "/ɪksˈpəʊz/",
    definition: "to make something visible by removing a covering",
    example: "The storm exposed the roots of the tree."
  },
  {
    word: "exposure",
    phonetic: "/ɪksˈpəʊʒə/",
    definition: "the state of being exposed to something",
    example: "Prolonged exposure to the sun can damage your skin."
  },
  {
    word: "express",
    phonetic: "/ɪksˈpres/",
    definition: "to show or communicate a feeling or opinion",
    example: "She expressed her gratitude for their help."
  },
  {
    word: "expression",
    phonetic: "/ɪksˈpreʃən/",
    definition: "the look on someone's face that shows their feelings",
    example: "His expression changed when he heard the news."
  },
  {
    word: "extend",
    phonetic: "/ɪksˈtend/",
    definition: "to make something longer or larger",
    example: "The company plans to extend its operations to Asia."
  },
  {
    word: "extension",
    phonetic: "/ɪksˈtenʃən/",
    definition: "the act of making something longer or larger",
    example: "The extension of the deadline gave us more time to finish the project."
  },
  {
    word: "extensive",
    phonetic: "/ɪksˈtensɪv/",
    definition: "covering a large area or involving many things",
    example: "The library has an extensive collection of books."
  },
  {
    word: "extent",
    phonetic: "/ɪksˈtent/",
    definition: "the degree to which something happens or is true",
    example: "I was surprised by the extent of the damage."
  },
  {
    word: "exterior",
    phonetic: "/ɪksˈtɪəriə/",
    definition: "the outside part of something",
    example: "The exterior of the building needs painting."
  },
  {
    word: "external",
    phonetic: "/ɪksˈtɜːnl/",
    definition: "happening or existing outside a person, organization, or place",
    example: "The company is facing external pressures from competitors."
  },
  {
    word: "extinct",
    phonetic: "/ɪksˈtɪŋkt/",
    definition: "no longer existing",
    example: "Dinosaurs became extinct millions of years ago."
  },
  {
    word: "extinguish",
    phonetic: "/ɪksˈtɪŋɡwɪʃ/",
    definition: "to make a fire stop burning",
    example: "The firefighters quickly extinguished the blaze."
  },
  {
    word: "extra",
    phonetic: "/ˈekstrə/",
    definition: "more than what is usual or necessary",
    example: "We need to hire extra staff for the holiday season."
  },
  {
    word: "extract",
    phonetic: "/ɪksˈtrækt/",
    definition: "to remove something from a place",
    example: "The dentist extracted her wisdom tooth."
  },
  {
    word: "extraordinary",
    phonetic: "/ɪkˈstrɔːdnəri/",
    definition: "very unusual or remarkable",
    example: "She has an extraordinary talent for music."
  },
  {
    word: "extreme",
    phonetic: "/ɪksˈtriːm/",
    definition: "very great in degree or intensity",
    example: "The weather reached extreme temperatures during the heatwave."
  },
  {
    word: "extremely",
    phonetic: "/ɪksˈtriːmli/",
    definition: "to a very high degree",
    example: "She was extremely happy when she got the job."
  },
    {
    word: "eye",
    phonetic: "/aɪ/",
    definition: "the organ of sight",
    example: "She has beautiful blue eyes."
  },
  {
    word: "eyebrow",
    phonetic: "/ˈaɪbraʊ/",
    definition: "the strip of hair above each eye",
    example: "She raised her eyebrow in surprise."
  },
  {
    word: "eyesight",
    phonetic: "/ˈaɪsaɪt/",
    definition: "the ability to see",
    example: "His eyesight is getting worse as he gets older."
  }
]
let answer = "hackstring"
let word_list = []
let word_p = 0

$(function() {
  //rand()
  load_config()
  render_list_selector()
  //check()
})

function set_auto_submit_on() {
  $("#auto-submit").removeClass("btn-outline-primary")
  $("#auto-submit").removeClass("btn-outline-secondary")

  $("#auto-submit").addClass("btn-outline-primary")
  $("#auto-submit").text("Auto Submit: On")
  localStorage.setItem("auto-submit", "on")
}

function set_auto_submit_off() {
  $("#auto-submit").removeClass("btn-outline-primary")
  $("#auto-submit").removeClass("btn-outline-secondary")

  $("#auto-submit").addClass("btn-outline-secondary")
  $("#auto-submit").text("Auto Submit: Off")
  localStorage.setItem("auto-submit", "off")
}


function set_show_label_on() {
  $("#show-label").removeClass("btn-outline-primary")
  $("#show-label").removeClass("btn-outline-secondary")

  $("#show-label").addClass("btn-outline-primary")
  $("#show-label").text("Label: On")
  $("#word-label").show()
  localStorage.setItem("show-label", "on")
}

function set_show_label_off() {
  $("#show-label").removeClass("btn-outline-primary")
  $("#show-label").removeClass("btn-outline-secondary")

  $("#show-label").addClass("btn-outline-secondary")
  $("#show-label").text("Label: Off")
  $("#word-label").hide()
  localStorage.setItem("show-label", "off")
}

function load_config() {
  if (localStorage.getItem("auto-submit") === "on") {
    set_auto_submit_on()
  } else {
    set_auto_submit_off()
  }
  if (localStorage.getItem("show-label") === "off") { // defalut open
    set_show_label_off()
  } else {
    set_show_label_on()
  }
}

function auto_sumbit_switch() {
  if (localStorage.getItem("auto-submit") === "on") {
    set_auto_submit_off()
  } else {
    set_auto_submit_on()
  }
}

function show_label_switch() {
  if (localStorage.getItem("show-label") === "on") {
    set_show_label_off()
  } else {
    set_show_label_on()
  }
}

function inputCheck(){
  let inp = $("#word-input").val()
  if (inp == answer) {
    $("#word-input").addClass("word-success")
    if (localStorage.getItem("auto-submit") === "on" ){
      setTimeout("submit()",250)
    }
  }else{
    $("#word-input").removeClass("word-success")
  }
}


function render_list_selector() {
  $.getJSON("/list_names", function(r, status) {
    if (r.error || status != "success") {
      console.log("error in render_list_selector")
      console.log(r.error_msg)
      setTimeout(render_list_selector, 1000)
    } else {
      if (!getCookie("last_word_list") || r["lists"].indexOf(getCookie("last_word_list")) == -1) {
        setCookie("last_word_list", r["lists"][0])
      }

      let last = getCookie("last_word_list")
      r["lists"].forEach(l => {
        if (l == last) {
          $('#word_list_selector').append('<option value="' + l +'" selected>'+ l + '</option>');
          set_word_list(l)
        } else {
          $('#word_list_selector').append('<option value="' + l +'">'+ l + '</option>');
        }
      });

      $("#word_list_selector").change(function() {
        let l = $("#word_list_selector").val()
        setCookie("last_word_list", l)
        set_word_list(l)
      });
    }
  });
}

function set_word_list(l) {
  $.getJSON("/word_list?name=" + l, function(r, status) {
    if (r.error || status != "success") {
      console.log("error in set_word_list")
      console.log(r.error_msg)
      alert(r.error_msg)
    } else {
      word_list = r["words"]
      word_list = shuffle(word_list)
      next_word()
    }
  });
}
function next_word() {
  word_p = (word_p + 1) % word_list.length
  let w = word_list[word_p]
  render(w.word, w.phonetic, w.explains, w.speech_url)
}

function replace_word(l, word) {
  let w = word[0].toUpperCase() + word.slice(1) // capitalise first letter
  return l.replace(w, "xxx")
}


function mark_part_of_speech(l){
  l=l.replace(/^n\./,'<em class="partofspeech">n.</em>')
  l=l.replace(/^adj\./,'<em class="partofspeech">adj.</em>')
  l=l.replace(/^vi\./,'<em class="partofspeech">vi.</em>')
  l=l.replace(/^vt\./,'<em class="partofspeech">vt.</em>')
  l=l.replace(/^v\./,'<em class="partofspeech">v.</em>')
  l=l.replace(/^int\./,'<em class="partofspeech">int.</em>')
  l=l.replace(/^adv\./,'<em class="partofspeech">adv.</em>')
  return l
}

function add_word_count(word, delta) {
    known_words = localStorage.getItem("known-words") || "{}"
    known_words = JSON.parse(known_words)
    if (!known_words[word]) { // word does not exist in known_words
        known_words[word] = delta
    } else {
        known_words[word] += delta
    }
    localStorage.setItem("known-words",JSON.stringify(known_words))
}

function get_word_count(word) {
    known_words = localStorage.getItem("known-words") || "{}"
    known_words = JSON.parse(known_words)
    if (!known_words[word]) { // word does not exist in known_words
        return 0
    } else {
        return known_words[word]
    }
}

function render(word, phonetic, explains, speech_url) {
  $("#phonetic").text(phonetic)
  $("#explains").html("")
  $.each(explains, function(_, l) {
    l = replace_word(l, word)
    l = mark_part_of_speech(l)
    $("#explains").append("<p>"+l+"</p>")
  })
  $("#speech").attr("src", speech_url)
  $("#youdao").attr("href", "https://dict.youdao.com/w/eng/" + word)
  $("#word-label").text(get_word_count(word)+"x")
  answer = word
  play()
}

function rand() {
  $.getJSON("/rand", function(r, status) {
    if (r.error || status != "success") {
      console.log(r.word)
      console.log(r.error_msg)
      alert(r.error_msg)
      answer = "hackstring";
    } else {
      render(r.word, r.phonetic, r.explains, r.speech_url)
    }
  });
}


function submit() {
  let inp = $("#word-input").val()
  if (inp == answer) {
    $("#word-input").val("")
    $("#word-input").removeClass("word-success")
    add_word_count(answer, 1)
    next_word()
  } else {
    play()
    $("#word-input").val("")
    $("#word-input").removeClass("word-success")
    $("#word-input").focus()
  }
}

function play() {
  let a = $("#speech")[0]
  a.currentTime = 0;
  a.play();
}

// code from: https://stackoverflow.com/a/6274398
function shuffle(array) {
  let counter = array.length;

  // While there are elements in the array
  while (counter > 0) {
      // Pick a random index
      let index = Math.floor(Math.random() * counter);

      // Decrease counter by 1
      counter--;

      // And swap the last element with it
      let temp = array[counter];
      array[counter] = array[index];
      array[index] = temp;
  }

  return array;
}

// cookie utilities from: https://stackoverflow.com/a/24103596
function setCookie(name,value,days) {
  var expires = "";
  if (days) {
      var date = new Date();
      date.setTime(date.getTime() + (days*24*60*60*1000));
      expires = "; expires=" + date.toUTCString();
  }
  document.cookie = name + "=" + (value || "")  + expires + "; path=/";
}
function getCookie(name) {
  var nameEQ = name + "=";
  var ca = document.cookie.split(';');
  for(var i=0;i < ca.length;i++) {
      var c = ca[i];
      while (c.charAt(0)==' ') c = c.substring(1,c.length);
      if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length,c.length);
  }
  return null;
}
function eraseCookie(name) {   
  document.cookie = name+'=; Max-Age=-99999999;';  
}

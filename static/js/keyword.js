/**
 * Created by IntelliJ IDEA.
 * User: soddy
 * Date: 2010-12-14
 * Time: 20:16:42
 * To change this template use File | Settings | File Templates.
 */
AnalysisPost = {};
(function(m){
    if(String.prototype.trim == undefined) {
        String.prototype.trim = function() {
            return this.replace(/^\s+(.*?)\s+$/,"$1");
        }
    }

    var log10 = function(x) {
      return Math.log(x)/Math.LN10;
    };
    m.stop_word = ",，.。“”\"'?？!！[]()［］（） 　:;：；/\\{}＼／｛｝\r\n\t《》、*&#…-abcdefghijklmnopqrstuvwxyz1234567890与的我个已是了着有可要和下这不任";
    var dict_db = [];
    m.setdict = function(v) {
        dict_db = v;
    }
    m.find_dict_db = function(v) {
        for(var i=0,d=dict_db,ilen=dict_db.length; i<ilen; i++) {
            if(d[i].word==v) {
                return i;
            }
        }
        return -1;
    };
    var CUT_LENGTH = 8,
        RANK_LIMIT = 1.5;
    var Keyword = function(pre, next){
        this.count = 0;
        this.pre = [];
        this.next = [];
        this.add(pre, next);
    };
    Keyword.prototype.add = function(pre, next){
        this.count ++;
        this.pre.push(pre);
        this.next.push(next);
    };
    Keyword.prototype.valid = function(){
        if((this.pre.length == 1 && this.pre[0] != "") ||
            (this.next.length == 1 && this.next[0] != "") ||
             this.count == 1) {
            return false;
        }
        return true;
    };
    Keyword.prototype.toString = function() {
        return this.count.toString();
    };
    Keyword.prototype.toValue = function() {
        return this.count;
    };
    var KeywordManager = function() {
        this.list = [];
        this.dict = {};
    };
    KeywordManager.prototype.addItem = function(pre, word, next) {
        if(this.dict[word] != undefined) {
            this.dict[word].add(pre, next);
        } else {
            this.dict[word] = new Keyword(pre, next);
        }
    };
    KeywordManager.prototype.add = function(char) {
        this.list.push(char);
    };
    KeywordManager.prototype.sync = function() {
        var len = this.list.length;
        for(var i=2; i < CUT_LENGTH; i++) {
            var pre = "";
            if (len >= i) {
                for(var j=0;j<len-1;j++) {
                    this.addItem(pre, this.list.slice(j, j+1).join(""), this.list[j+1]);
                    pre = this.list[j]
                }
                this.addItem(pre, this.list.slice(len-i).join(""), "")
            } else {
                break;
            }
        }
        this.list = [];
    };
    m.findkeyword = function(str) {
        var word = {},
            word_list = {},
            trash = [],
            word_list_finally = {},
            word_list2 = [],
            no_login_word_list=[],
            temp = [],
            result = [],
            keyword_manager = new KeywordManager(),
            kdic = keyword_manager.dict,
            total_len = 0,
            input = str.replace("\r", "").split("\n"),
            inputlen = input.length,
            rank = 0;
        for(var i=0; i < inputlen; i++) {
            line = input[i].trim().split("");
            total_len += line.length;
            for(var j = 0, jlen = line.length; j <= jlen; j++) {
                if(m.stop_word.indexOf(line[j]) != -1) {
                    keyword_manager.sync();
                } else {
                    keyword_manager.add(line[j]);
                }
            }
        }
        keyword_manager.sync();

        for(var k in kdic) {
            if(kdic[k].valid()) {
                word_list[k] = kdic[k].toValue();
            }
        }
        var add = function(word, v) {
            if(word_list[word] != undefined) {
                if(v/word_list[word] > 0.618) {
                    trash.push(word);
                } else {
                    return false;
                }
            }
        }, intrash = function(v) {
            for(var i=0,ilen = trash.length; i<ilen; i++) {
                if(trash[i] == v) {
                    return true;
                }
            }
            return false;
        }
        for(var k in word_list) {
            if(k.length > 2) {
                if(add(k.substring(1), word_list[k]) && add(k.substring(0,-1), word_list[k])) {
                    if(!intrash(k)) {
                        word_list_finally[k] = word_list[k];
                    }
                }
            } else if (!intrash(k)) {
                word_list_finally[k] = word_list[k];
            }
        }
        var numb = -1;
        for(var k in word_list_finally) {
            numb = m.find_dict_db(k);
            if(numb != -1) {
                rank = log10(word_list_finally[k]/dict_db[numb].idf);
                word_list2.push([k, rank]);
            } else {
                rank = word_list_finally[k] * log10(k.length);
                if(rank > 1.7) {
                    no_login_word_list.push([k, rank]);
                }
            }
        }
        var sorter = function(x,y){
            return x[1] > y[1] ? -1 :
                                  x[1] == y[1] ?
                                          0 : 1;
        };
        word_list2.sort(sorter);
        no_login_word_list.sort(sorter);
        console.log(word_list2);
        console.log(no_login_word_list);

        keyword_no=total_len/300+3;
        temp = Array.prototype.concat.apply(word_list2.slice(0, keyword_no), no_login_word_list);
        for(var i =0, ilen = temp.length; i<ilen; i++) {
            result.push(temp[i][0]);
        }
        return result;
    };
})(AnalysisPost);
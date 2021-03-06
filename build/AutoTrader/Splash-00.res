tcl86t.dll      tk86t.dll       tk              __splash              ?  ?  ?   ?   Xtk\ttk\utils.tcl tk\license.terms tk\tk.tcl tk\ttk\cursors.tcl tcl86t.dll tk86t.dll tk\ttk\fonts.tcl tk\ttk\ttk.tcl tk\text.tcl proc _ipc_server {channel clientaddr clientport} {
set client_name [format <%s:%d> $clientaddr $clientport]
chan configure $channel \
-buffering none \
-encoding utf-8 \
-eofchar \x04 \
-translation cr
chan event $channel readable [list _ipc_caller $channel $client_name]
}
proc _ipc_caller {channel client_name} {
chan gets $channel cmd
if {[chan eof $channel]} {
chan close $channel
exit
} elseif {![chan blocked $channel]} {
if {[string match "update_text*" $cmd]} {
global status_text
set first [expr {[string first "(" $cmd] + 1}]
set last [expr {[string last ")" $cmd] - 1}]
set status_text [string range $cmd $first $last]
}
}
}
set server_socket [socket -server _ipc_server -myaddr localhost 0]
set server_port [fconfigure $server_socket -sockname]
set env(_PYIBoot_SPLASH) [lindex $server_port 2]
image create photo splash_image
splash_image put $_image_data
unset _image_data
proc canvas_text_update {canvas tag _var - -} {
upvar $_var var
$canvas itemconfigure $tag -text $var
}
package require Tk
set image_width [image width splash_image]
set image_height [image height splash_image]
set display_width [winfo screenwidth .]
set display_height [winfo screenheight .]
set x_position [expr {int(0.5*($display_width - $image_width))}]
set y_position [expr {int(0.5*($display_height - $image_height))}]
frame .root
canvas .root.canvas \
-width $image_width \
-height $image_height \
-borderwidth 0 \
-highlightthickness 0
.root.canvas create image \
[expr {$image_width / 2}] \
[expr {$image_height / 2}] \
-image splash_image
wm attributes . -transparentcolor magenta
.root.canvas configure -background magenta
pack .root
grid .root.canvas -column 0 -row 0 -columnspan 1 -rowspan 2
wm overrideredirect . 1
wm geometry . +${x_position}+${y_position}
wm attributes . -topmost 1
raise .?PNG

   IHDR         \r?f  ?IDATx???ˏ$?Uƿs#??]53?F?6???"?????x?12$6,???3F?????AH???`??ǚ?i?A?U?X??OwUwe???>??#3###2??~?Vv>*???????)_?ɗ??,1?? B????14 B2?@H?? ? !C $ch ?d?????14 B2?@H?? ? !C $ch ?d?????14 B2?@H?? ? !C $ch ?d?????14 B2??ե??O?Ç???wB???=9_?<Ξv??&@??ٮ7`/?!????U??zO?6???`?d-???ψ?\2?t???????>?????_?z???Û2 ;?X%???ٓC??FG????*?N???`??\?==½o????G??"?) Fd??k }{?x??????Wu?Ki?ɛAM?Ȏ?? ?_%|????Z???'?Z?? $???ދ?&@???`??;??1?w?{???
???8?+ ????@P??&@????K?z|?????#???????C??/?:]/0BvI>u =ů??x_????z?????Z??`]q??B??(!?Q8=j???$d}?0?5?(`???}??q~?O? ????`51???F8?)|???o/??%?? R?x???ٓC??Κ?\?_??????m?? ?Bq?????w_??Ǉ??@??a???m ]??"?[???9½{sm??^[?P?Ƹa?,D*????#???ם?????L??5?Ua?u=?????????}j *P#???~	????}|?z}?3 ?????4?u??{~'??? `-t^??߈??? 
<??E???7q???*Ӑ??&u?L??3?5?ugO?p??5???c????K?Q?q??Q? ?=y??[m??x????m???Y>L??j@/??,|%??Q??$?E	
.?????/^???????)???N?ECd
?????Ƙ??R??7??y?' ??y	'???8?d???r"p#u????X9H??j@_???~????????\?-?в?^?PUu????=???????&?2?x`?0???o ?Ŀ阿Y???^?!Z??????o?>?=Y!~? ~????%??p?&@F?r??r????0??*???r5 :/????????<{?r??(-??????ɊB?????5???k???????x????쬟????0`|2@\@M?!Hr42?? V?_m??o?????Ϟ?????????k펝?0?q??
?ʇ?G?IB?\>???o]?j?9????`>@?ֺ???@`?	?ϑ?0??hdS.??Cد????/ ??p??r H??º??@`?????c ?*?? ~????  ??)??\@54hG?l??0?}?\??f?Uй??????B?? U?`k?9 C??[?c???(?3???????2
???P?? aVz܅?m? . ??p?????t??R@q??_*?8
 d(?k -ab??O`d???-T?_?.b%??Hؖ?KCa? !????7a???\@???!1??6N?3I5_?@?l???43??%?ZZ??????>j?o???B6`?`????Z)~?L? ???,?R?`V?~׎!#?????=?4???(?;????8???Y3?xHhds?? ?6??^?@? B?_?Vt??*????? s??????"b?????@?2?? ? ?a?L@Q?hTTI@BFfw@?WĤ??-Ak?1?2??Ȇ?? (???Y[?Q?ڸ?c??!?}X!~'?|??%?j?~!???kI??q?rW????VN????P+?q?????!#??R?}?m??_?T???%??i2?i?? ? ?=??<???????;?BrE?>H??ڸ?a¯???k???????u?V??Mm???D?~2.??Iؿ??jc??!?2??6?-t??e?2,n߶?Cr.??P?S???B&`?S????ǥ'?<?#?؎a?`j????B&g???R??\F6W????-??O?P??@ݓ1\!????';`?Jz??????'?!???kz?_???gO?p???p~v4?3(~B?a=??!??&?O???`?Oȕc?r?e?G??,?==?!????S/?W??U?8{:A?O?2:?Գl?J?
'?'???]???\V+(h?? ?d??Z???KF?@M??f?C???????/W?t{???b{1?}>?>??|v??9??9???g?r???.?/`???]?W??W??쥑!y2?(????e??C?vn?/??K؋9?b???????B?h^???z??oP?~e?@H?,7?Ec?$?Y?? TUh.?o?e]?^??b;/???p?1w>?n?g????/?ɘ^@k????DOl???m颀(?????.*x>?"?6?????~?/Q?!c?? ??Q? ?j~??W? 'x/? ??X???,1?M???/(~B&b?t??q??j??ո???%4?#Hrnx????B5<ǝo.7?ӗ???'dB?`???z՟?:_??F?Ds??(?m-Kgebe5?7???'?????ȻKIY?????|ϯ
?$?Ur0\??_?^>??g?*??Y??w??Ȯ??dH?i?f???բEU??d}?M???4??&~T?)?rs???\x틑x??m0??#Po??ڥ?ZAl?s?????`???T??ݩ?????a??	j7??s3? A?A?1b渉>?c??3?6?JᏍ;L?????2??5X?`?'?z4?x?????_??׾g?g??j??>???l?/?|B<aR????H??^??v#٧`d?Z????)
w=+???
????rP?????k????X?u???a??@? b]#/?4?? ??1???wb????֖P[?	؋??? <>/??2?4gbb?'#[?1 jQLk??~?;?K?d??ŉ?@
'ps0?y? ?????`?_C1{?]?????: ?㰈!??&Æ @-???p?0??"	=!?D?+`?ª????z?q???:D?~?*Qbo??G ?
$^@?o????z}?!???ok_??>????e?)??Xx^ulL??럓?H???@Fd??t??U??bx_?k?N??
-|`??????8*?????[?B{i??(??\H@,?U?H??4????H??(??r?1G??????3??F??R?GL&?3??2??Х? ?k??
?b!@)Pc ?W-?i????D??P?H?Xb?^W?F??iT~۬T+?iI4g*<???!᠄p?$??Fq?o`
?
S$?@?#??4?z'?? t??:?? b ???E?;W?[??!?o
??p?g?Tc?c?o[)?n???K???????]N?@??I?=?? 3?f????Ę???T?%?	2? tA?{~U?`5f???E?gM{?М??? ?& x?C(?h?!??i??gD?&%4D??????ҡ?O?I@??~??p??_?_$??4@?/?I?5?b8@S ?30	X`Tm?XS?C??'O?????!?0g?
??Ә?? ?????w?'օ?Қ???l?#??Q??8{??~?T=}a ??r0????_#:H?Ԇh???ȚC?D(?7u=??ѽ @?z?/????,5a?P?7?q? ???с??x3Qq???.??jebm?A(AS??w=
??N??0?#0n?V?\?Â?,??%?LB?Q??n??B? V@?|?!??kp??:????P?0I6??????g?#??Z??VR??J??_?P??y??:??~? -

?n7w?qG??%?ĩ@IB?*?w???'??7?٬>Hg
>!UNB:?? Y?nh??5 ??:w???U?????Q6>ɋ&??;v'?	??	5??^?0й????%?6N?E?0l?(h????
x?H%?Px??A??i~?1EX3?h]???O??8X9.??@?????g?D???O?	?2>A?Ǵ?ߑ?5??P??]??_??`[e?C???e?@????????a?$??aJ?'?b??A?V???v?"??Y4̪?Q?Q,???Ò?????nH 0I???@h?"?4A?? ?L~?آ*?????X  UwW?kzSC??L??k3?
?_sF`^?˄??E5??@?.@??^?+#????D?\@?B?o?Uں{Ub??CN؊?G??/?ow??>?f??gE<??zȯ??o?????U_??!?ZG??h@{`?,??????I.!!(?q?\8???!!#?V????qsbN?????|\??!??,J???P(>?P?????&?}??}ү?C?@4 ]` ?w:???o?05??(ȅ??(??qX???? P$S???????g?OƦ?Z ?;?zP?	??u???q?̛@??>?Zq?P??K*~?1X-	?K???Ȇ???@C???d8?j??Ւ???(`fIDp?????4rHz?곤?!L??????qL?}?9 W?Ky?	??A#?????O??f????????I??|$???	}??xK?H
?(?TF+????8?3!BC??@???<U???ғ??15??"\?Ui:TW???B???GJw????,???t_???Eu???~?cv.I???ɉO??`R$??̸$a??E\+?("dD?W.z8??Ơ?&??? ">
?	5߰ĕ?q!~,?q?%??e???Va?????e??j	?x;93P?LE???c	qRT%?==??? ?4N/??20??kD?j??,??|W?*?_?^>?,???,?:?8??qϿ?`|q?????????0?)??"?Z#P?d?ِ?g??#?0MXZ?? ?Bi?(ܢg @??~m`k?/)???n5??F ????iү???z}?X???#G??|?ZCP3????}q?Y?E?\??????G=ٷ? IF??'L2H??j????lA?MS??h#?xY?q#?E&h? uuՃ?z??k???s???????z??,??? ?v??^ d W??da???YKާUs Ꝍ??? ??A?g	??)=1?9 CȏjFA??M??????ז?P ?-hܮs??G?A???Xl? :*k???ғuH??ioL.bQ??1??QOеz?Z????VB??_W=????`Y??B@?~<K?O?Uf>(D@???v???3p?s???i??1??[? :M  ?i?B/?o? ??|????V?v?% ?u??C??AHDވ?'??!#1?,?Z#??VB??????w?,3??c?軞G????j@g?p#" ?x3??A]?5??'Z?U?%z?`?6?~2%?@k.??????z?44/?g?[???\?ߚ-h?&?乄???f?^?@*?x끛?3:7??Y2[.n?"L^?!d???B?*4 B2?@H?? ? !C $ch ?d?????14 B2?@H?? ? !??Հ?'7p??c?z??Z???ۏG???????I?}{?????񯟮ܷ??3ݞ!?߄!m"}?2?۾lz?vy?W?5x??k ??b?k^??WG???^???4???X????vǤ?K?r;?????Zģ?^???S?z??F"?&???a?v??????_????Z?Kهc???@?}??w&ܡ?ܹ?Q??5|y??Y??ǿ~o/k@ǷOk?????ęĭw֌`???ӷ???9=9ƃ??p|?w????ڔ1?Ģ}==??o??}?tzr?e2}?k?>?>l? ?hG??ۏ{}!QXk]??????ģ?^??ɍ??O????uG]???m>=9ƃw??v?M,?f?x}1ݹ?????~wc???8?}?J0|?ǷO]???ݏp??????????W?{????3??~?;w?"?+^Qgm"????|5~΃w_[??a;B?;e???M?q&7?􀆃9dLth????????o??????w?&?wq
`?	c?VnC?q_?7??]??p?]???o?????GKa??N??6?4??vu?>0??eRH???EO?f?$ݟM?j5???hiHv=??6??????'??nϤp?A???v?:Y?>l:????C??I?=7?m0qp?>%???Ui?]??\?(`p?o?m?ͬ?n??6eʡ?d?l<Ue??F ?ӏ???%???}?s??M????:?x]?3?$???V???fjc?l??޷???x|n???>???0r??e?B?>!q??;????%]?2?t띇[?]w?V????^؇6???р????Oy??0??	Yn??N^s寗 ?́u??S)w??D(?ª???a??@?:????	????&???:?򪷉?ۧK?-}?T?x??:?!?==???/3?'7F?¶?#?s?~m̹?n?/??M4d??T?x(?'?%z?l+?3???????~=??4???H>??&?1?1ʨ0d>|J??|o`?)?????KԪ??{u?5	??&??Z?Ø?xF5?!??}???rȩ???z??HCC?&w??ea?TmbSbT??Ȫ????&?X??.??8d+??#W?????h??4&i?c??1???m?S?c?M? 6YI?H?ck???S
i?(`_V?u5о?7E?ؔ?X??[_?M????g k$z?,OZ???t?m]~҉UL]??.??o??h??/??d?1ޔQ`??0??iCX??-??'?X?>M??~?֙u?lCh??Nu??MX???(???P%~????_??B??	??NOn?k_zc/ş????l????W??؟?ct$}?h?^vYX0??%~?KoĐ?k?|?`v!???#=?k؎[o??Մ7??????߃w??Z;u?XE??ا<????9?c????Q]VL ?j;=?n?8??2?ܽ????i}??m??ml?&?
t[m?k_zc???{l?7?\?)c???c<@?ԏ?d[5Ut|?1??~???n??p??MBذ?@wt??1?w?v??=t.<?܃w_???c?mb]Q⶙???|?'_??ߕr)????14 B2?@H?? ? !C $ch ?d?????14 B2?@H?? ? !C $ch ?d?????14 B2?@H?? ? !C $ch ?d?????14 B2?@H?? ? !C $ch ?d?????14 B2?@H?? ? !C $ch ?d?????14 B2?@H?? ? !C $ch ?d?????14 B2?@H?? ? !C $ch ?d?????14 B2?@H?? ? !C $ch ?d?????14 B2?@H?? ? !C $ch ?d?????14 B2?@H?? ? !C $ch ?d?????0}???    IEND?B`??PNG

   IHDR         \r?f  ?IDATx???ˏ$?Uƿs#??]53?F?6???"?????x?12$6,???3F?????AH???`??ǚ?i?A?U?X??OwUwe???>??#3###2??~?Vv>*???????)_?ɗ??,1?? B????14 B2?@H?? ? !C $ch ?d?????14 B2?@H?? ? !C $ch ?d?????14 B2?@H?? ? !C $ch ?d?????14 B2??ե??O?Ç???wB???=9_?<Ξv??&@??ٮ7`/?!????U??zO?6???`?d-???ψ?\2?t???????>?????_?z???Û2 ;?X%???ٓC??FG????*?N???`??\?==½o????G??"?) Fd??k }{?x??????Wu?Ki?ɛAM?Ȏ?? ?_%|????Z???'?Z?? $???ދ?&@???`??;??1?w?{???
???8?+ ????@P??&@????K?z|?????#???????C??/?:]/0BvI>u =ů??x_????z?????Z??`]q??B??(!?Q8=j???$d}?0?5?(`???}??q~?O? ????`51???F8?)|???o/??%?? R?x???ٓC??Κ?\?_??????m?? ?Bq?????w_??Ǉ??@??a???m ]??"?[???9½{sm??^[?P?Ƹa?,D*????#???ם?????L??5?Ua?u=?????????}j *P#???~	????}|?z}?3 ?????4?u??{~'??? `-t^??߈??? 
<??E???7q???*Ӑ??&u?L??3?5?ugO?p??5???c????K?Q?q??Q? ?=y??[m??x????m???Y>L??j@/??,|%??Q??$?E	
.?????/^???????)???N?ECd
?????Ƙ??R??7??y?' ??y	'???8?d???r"p#u????X9H??j@_???~????????\?-?в?^?PUu????=???????&?2?x`?0???o ?Ŀ阿Y???^?!Z??????o?>?=Y!~? ~????%??p?&@F?r??r????0??*???r5 :/????????<{?r??(-??????ɊB?????5???k???????x????쬟????0`|2@\@M?!Hr42?? V?_m??o?????Ϟ?????????k펝?0?q??
?ʇ?G?IB?\>???o]?j?9????`>@?ֺ???@`?	?ϑ?0??hdS.??Cد????/ ??p??r H??º??@`?????c ?*?? ~????  ??)??\@54hG?l??0?}?\??f?Uй??????B?? U?`k?9 C??[?c???(?3???????2
???P?? aVz܅?m? . ??p?????t??R@q??_*?8
 d(?k -ab??O`d???-T?_?.b%??Hؖ?KCa? !????7a???\@???!1??6N?3I5_?@?l???43??%?ZZ??????>j?o???B6`?`????Z)~?L? ???,?R?`V?~׎!#?????=?4???(?;????8???Y3?xHhds?? ?6??^?@? B?_?Vt??*????? s??????"b?????@?2?? ? ?a?L@Q?hTTI@BFfw@?WĤ??-Ak?1?2??Ȇ?? (???Y[?Q?ڸ?c??!?}X!~'?|??%?j?~!???kI??q?rW????VN????P+?q?????!#??R?}?m??_?T???%??i2?i?? ? ?=??<???????;?BrE?>H??ڸ?a¯???k???????u?V??Mm???D?~2.??Iؿ??jc??!?2??6?-t??e?2,n߶?Cr.??P?S???B&`?S????ǥ'?<?#?؎a?`j????B&g???R??\F6W????-??O?P??@ݓ1\!????';`?Jz??????'?!???kz?_???gO?p???p~v4?3(~B?a=??!??&?O???`?Oȕc?r?e?G??,?==?!????S/?W??U?8{:A?O?2:?Գl?J?
'?'???]???\V+(h?? ?d??Z???KF?@M??f?C???????/W?t{???b{1?}>?>??|v??9??9???g?r???.?/`???]?W??W??쥑!y2?(????e??C?vn?/??K؋9?b???????B?h^???z??oP?~e?@H?,7?Ec?$?Y?? TUh.?o?e]?^??b;/???p?1w>?n?g????/?ɘ^@k????DOl???m颀(?????.*x>?"?6?????~?/Q?!c?? ??Q? ?j~??W? 'x/? ??X???,1?M???/(~B&b?t??q??j??ո???%4?#Hrnx????B5<ǝo.7?ӗ???'dB?`???z՟?:_??F?Ds??(?m-Kgebe5?7???'?????ȻKIY?????|ϯ
?$?Ur0\??_?^>??g?*??Y??w??Ȯ??dH?i?f???բEU??d}?M???4??&~T?)?rs???\x틑x??m0??#Po??ڥ?ZAl?s?????`???T??ݩ?????a??	j7??s3? A?A?1b渉>?c??3?6?JᏍ;L?????2??5X?`?'?z4?x?????_??׾g?g??j??>???l?/?|B<aR????H??^??v#٧`d?Z????)
w=+???
????rP?????k????X?u???a??@? b]#/?4?? ??1???wb????֖P[?	؋??? <>/??2?4gbb?'#[?1 jQLk??~?;?K?d??ŉ?@
'ps0?y? ?????`?_C1{?]?????: ?㰈!??&Æ @-???p?0??"	=!?D?+`?ª????z?q???:D?~?*Qbo??G ?
$^@?o????z}?!???ok_??>????e?)??Xx^ulL??럓?H???@Fd??t??U??bx_?k?N??
-|`??????8*?????[?B{i??(??\H@,?U?H??4????H??(??r?1G??????3??F??R?GL&?3??2??Х? ?k??
?b!@)Pc ?W-?i????D??P?H?Xb?^W?F??iT~۬T+?iI4g*<???!᠄p?$??Fq?o`
?
S$?@?#??4?z'?? t??:?? b ???E?;W?[??!?o
??p?g?Tc?c?o[)?n???K???????]N?@??I?=?? 3?f????Ę???T?%?	2? tA?{~U?`5f???E?gM{?М??? ?& x?C(?h?!??i??gD?&%4D??????ҡ?O?I@??~??p??_?_$??4@?/?I?5?b8@S ?30	X`Tm?XS?C??'O?????!?0g?
??Ә?? ?????w?'օ?Қ???l?#??Q??8{??~?T=}a ??r0????_#:H?Ԇh???ȚC?D(?7u=??ѽ @?z?/????,5a?P?7?q? ???с??x3Qq???.??jebm?A(AS??w=
??N??0?#0n?V?\?Â?,??%?LB?Q??n??B? V@?|?!??kp??:????P?0I6??????g?#??Z??VR??J??_?P??y??:??~? -

?n7w?qG??%?ĩ@IB?*?w???'??7?٬>Hg
>!UNB:?? Y?nh??5 ??:w???U?????Q6>ɋ&??;v'?	??	5??^?0й????%?6N?E?0l?(h????
x?H%?Px??A??i~?1EX3?h]???O??8X9.??@?????g?D???O?	?2>A?Ǵ?ߑ?5??P??]??_??`[e?C???e?@????????a?$??aJ?'?b??A?V???v?"??Y4̪?Q?Q,???Ò?????nH 0I???@h?"?4A?? ?L~?آ*?????X  UwW?kzSC??L??k3?
?_sF`^?˄??E5??@?.@??^?+#????D?\@?B?o?Uں{Ub??CN؊?G??/?ow??>?f??gE<??zȯ??o?????U_??!?ZG??h@{`?,??????I.!!(?q?\8???!!#?V????qsbN?????|\??!??,J???P(>?P?????&?}??}ү?C?@4 ]` ?w:???o?05??(ȅ??(??qX???? P$S???????g?OƦ?Z ?;?zP?	??u???q?̛@??>?Zq?P??K*~?1X-	?K???Ȇ???@C???d8?j??Ւ???(`fIDp?????4rHz?곤?!L??????qL?}?9 W?Ky?	??A#?????O??f????????I??|$???	}??xK?H
?(?TF+????8?3!BC??@???<U???ғ??15??"\?Ui:TW???B???GJw????,???t_???Eu???~?cv.I???ɉO??`R$??̸$a??E\+?("dD?W.z8??Ơ?&??? ">
?	5߰ĕ?q!~,?q?%??e???Va?????e??j	?x;93P?LE???c	qRT%?==??? ?4N/??20??kD?j??,??|W?*?_?^>?,???,?:?8??qϿ?`|q?????????0?)??"?Z#P?d?ِ?g??#?0MXZ?? ?Bi?(ܢg @??~m`k?/)???n5??F ????iү???z}?X???#G??|?ZCP3????}q?Y?E?\??????G=ٷ? IF??'L2H??j????lA?MS??h#?xY?q#?E&h? uuՃ?z??k???s???????z??,??? ?v??^ d W??da???YKާUs Ꝍ??? ??A?g	??)=1?9 CȏjFA??M??????ז?P ?-hܮs??G?A???Xl? :*k???ғuH??ioL.bQ??1??QOеz?Z????VB??_W=????`Y??B@?~<K?O?Uf>(D@???v???3p?s???i??1??[? :M  ?i?B/?o? ??|????V?v?% ?u??C??AHDވ?'??!#1?,?Z#??VB??????w?,3??c?軞G????j@g?p#" ?x3??A]?5??'Z?U?%z?`?6?~2%?@k.??????z?44/?g?[???\?ߚ-h?&?乄???f?^?@*?x끛?3:7??Y2[.n?"L^?!d???B?*4 B2?@H?? ? !C $ch ?d?????14 B2?@H?? ? !??Հ?'7p??c?z??Z???ۏG???????I?}{?????񯟮ܷ??3ݞ!?߄!m"}?2?۾lz?vy?W?5x??k ??b?k^??WG???^???4???X????vǤ?K?r;?????Zģ?^???S?z??F"?&???a?v??????_????Z?Kهc???@?}??w&ܡ?ܹ?Q??5|y??Y??ǿ~o/k@ǷOk?????ęĭw֌`???ӷ???9=9ƃ??p|?w????ڔ1?Ģ}==??o??}?tzr?e2}?k?>?>l? ?hG??ۏ{}!QXk]??????ģ?^??ɍ??O????uG]???m>=9ƃw??v?M,?f?x}1ݹ?????~wc???8?}?J0|?ǷO]???ݏp??????????W?{????3??~?;w?"?+^Qgm"????|5~΃w_[??a;B?;e???M?q&7?􀆃9dLth????????o??????w?&?wq
`?	c?VnC?q_?7??]??p?]???o?????GKa??N??6?4??vu?>0??eRH???EO?f?$ݟM?j5???hiHv=??6??????'??nϤp?A???v?:Y?>l:????C??I?=7?m0qp?>%???Ui?]??\?(`p?o?m?ͬ?n??6eʡ?d?l<Ue??F ?ӏ???%???}?s??M????:?x]?3?$???V???fjc?l??޷???x|n???>???0r??e?B?>!q??;????%]?2?t띇[?]w?V????^؇6???р????Oy??0??	Yn??N^s寗 ?́u??S)w??D(?ª???a??@?:????	????&???:?򪷉?ۧK?-}?T?x??:?!?==???/3?'7F?¶?#?s?~m̹?n?/??M4d??T?x(?'?%z?l+?3???????~=??4???H>??&?1?1ʨ0d>|J??|o`?)?????KԪ??{u?5	??&??Z?Ø?xF5?!??}???rȩ???z??HCC?&w??ea?TmbSbT??Ȫ????&?X??.??8d+??#W?????h??4&i?c??1???m?S?c?M? 6YI?H?ck???S
i?(`_V?u5о?7E?ؔ?X??[_?M????g k$z?,OZ???t?m]~҉UL]??.??o??h??/??d?1ޔQ`??0??iCX??-??'?X?>M??~?֙u?lCh??Nu??MX???(???P%~????_??B??	??NOn?k_zc/ş????l????W??؟?ct$}?h?^vYX0??%~?KoĐ?k?|?`v!???#=?k؎[o??Մ7??????߃w??Z;u?XE??ا<????9?c????Q]VL ?j;=?n?8??2?ܽ????i}??m??ml?&?
t[m?k_zc???{l?7?\?)c???c<@?ԏ?d[5Ut|?1??~???n??p??MBذ?@wt??1?w?v??=t.<?܃w_???c?mb]Q⶙???|?'_??ߕr)????14 B2?@H?? ? !C $ch ?d?????14 B2?@H?? ? !C $ch ?d?????14 B2?@H?? ? !C $ch ?d?????14 B2?@H?? ? !C $ch ?d?????14 B2?@H?? ? !C $ch ?d?????14 B2?@H?? ? !C $ch ?d?????14 B2?@H?? ? !C $ch ?d?????14 B2?@H?? ? !C $ch ?d?????14 B2?@H?? ? !C $ch ?d?????14 B2?@H?? ? !C $ch ?d?????0}???    IEND?B`?
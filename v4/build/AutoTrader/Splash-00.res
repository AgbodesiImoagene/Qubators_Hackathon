tcl86t.dll      tk86t.dll       tk              __splash              �  
  �   �   Xtk\ttk\cursors.tcl tk\tk.tcl tk\ttk\utils.tcl tcl86t.dll tk\ttk\fonts.tcl tk\text.tcl tk\ttk\ttk.tcl tk86t.dll tk\license.terms proc _ipc_server {channel clientaddr clientport} {
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
raise .�PNG

   IHDR         k�XT   PLTE���m��l��	�����j�������f��
��	��������^�������]���ُ��]����\�����i�����������]��g��]��k��
����h��k�������k����k�������l�����������������������}����]�����]�������]�����]��e�����������������������Ӓ�����Q����I}�MMMNNNOOOPPPQQQRRRSSSTTTUUUVVVWWWXXXYYYZZZ[[[\\\]]]^^^___```aaabbbcccdddeeefffggghhhiiijjjkkklllmmmnnnooopppqqqrrrssstttuuuvvvwwwxxxyyyzzz{{{|||}}}~~~������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������xO�6  �IDATx�훉��&����Nvr)��n��}o�;�����DB�$��U�������t�@7h��                     �0�Zځ��xzi��\�� �g�g-@���\��]ڋ�X�� 2���ե�}oiO�a����znI�NL5�?p����tZ.��U|���e}:%c������+{u:��� Ճ��_]گQ=\S��_ׯ-��i�� ��o��#@��
p�V��䀷�T�G����4����}�g1��׏U�gP6��/?	�����T�N�_|xor�������e2�u|���G������������$8���s���*`������ؽ�|�/zT����$��翝� ,�\B��9����_h�����2T��Rs@D��Vb��# &�Kʪq��㓥}N��4b�il�����QT���0.���r��>���ӥ=O���1*{���_� ��߲�7�#���_��?�ud�:0�ܧ�!�_�����X�?�ǟ�Kу���'2�濎���g)�Ϸ
T��?�kL��� E��d��z��$�?�&�������X��&�$�,�g*����d���InU ���G@����߿&@���� ��$��2�:�K�)׿�/W �߿G�I8F���>J���1�x���W��۟'�|�]��s[	*6�'�?�*`� U��L�&]�Y
�Ï��Z:�x~�%a���_�Ɵ�'2�ߒƟ� 	�_GnS������v�r{������kOloo��v�ono��������2n��n�������7�-           S���̾�����E{�{#�u'5��FDc�&蝌G��H���s� ��:
�k�y#[qrFO�]�T^>k8�F�t� ��N�9��0�Y�c�7�9�x/��Ro�X�1e8��ƴ�X����p�v��1�/��*wD7c8 ��v�`�ύcn�A�
"�q��h����1@k^&F �y�QXv�˭L?6{QYe�Ν6�Ny�r� �lL3�̀��s$�ު÷9�t�Ǳ! s��O�P?���Oc���(�f��v� ܕ�GU"��kzZ1t׎"@?�4��p�a$��A�~js���{<L g�xQ�_s;T gJ�ڟ@�?}�A� M� Ή�G�;4.�Gi͒_ sɠ\n��E�
@�"�r��cp�[� �:ֱ`%�	@�ӆ�T�S ϊ]�xf�0�R��� ��3JH& ���6�w|��f��D1x��?�KǕ�	��9�i8 n��f�G���A�͉2��5��j�Q�dt�M-7-)Mӣ�]G3%@��MG���!V��:�6 #.
��}%�LK��2H�oB�ݤ�:]�P����uk�IƄ�kw�x����(|X�RO��
�d�����h[g�E�u�w!$�w<FPC/V���o8 *W���W���\?�_	j�x����瘿D�`�`َYRI�W��:��K�	+��^1�;��*�v��Ë��rT�1�d���^@5a�����nfr��1�]Ŕ$ݫ^!��Z��x!��������`����tnɅ'.���\����q�d�]ؒ��ou3�(������ֈ�t�V���{�����Sl\mS]�\�p�q{�m�3<�w�ٌ5<�                                                    o�= |��,    IEND�B`��PNG

   IHDR         k�XT   PLTE���m��l��	�����j�������f��
��	��������^�������]���ُ��]����\�����i�����������]��g��]��k��
����h��k�������k����k�������l�����������������������}����]�����]�������]�����]��e�����������������������Ӓ�����Q����I}�MMMNNNOOOPPPQQQRRRSSSTTTUUUVVVWWWXXXYYYZZZ[[[\\\]]]^^^___```aaabbbcccdddeeefffggghhhiiijjjkkklllmmmnnnooopppqqqrrrssstttuuuvvvwwwxxxyyyzzz{{{|||}}}~~~������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������xO�6  �IDATx�훉��&����Nvr)��n��}o�;�����DB�$��U�������t�@7h��                     �0�Zځ��xzi��\�� �g�g-@���\��]ڋ�X�� 2���ե�}oiO�a����znI�NL5�?p����tZ.��U|���e}:%c������+{u:��� Ճ��_]گQ=\S��_ׯ-��i�� ��o��#@��
p�V��䀷�T�G����4����}�g1��׏U�gP6��/?	�����T�N�_|xor�������e2�u|���G������������$8���s���*`������ؽ�|�/zT����$��翝� ,�\B��9����_h�����2T��Rs@D��Vb��# &�Kʪq��㓥}N��4b�il�����QT���0.���r��>���ӥ=O���1*{���_� ��߲�7�#���_��?�ud�:0�ܧ�!�_�����X�?�ǟ�Kу���'2�濎���g)�Ϸ
T��?�kL��� E��d��z��$�?�&�������X��&�$�,�g*����d���InU ���G@����߿&@���� ��$��2�:�K�)׿�/W �߿G�I8F���>J���1�x���W��۟'�|�]��s[	*6�'�?�*`� U��L�&]�Y
�Ï��Z:�x~�%a���_�Ɵ�'2�ߒƟ� 	�_GnS������v�r{������kOloo��v�ono��������2n��n�������7�-           S���̾�����E{�{#�u'5��FDc�&蝌G��H���s� ��:
�k�y#[qrFO�]�T^>k8�F�t� ��N�9��0�Y�c�7�9�x/��Ro�X�1e8��ƴ�X����p�v��1�/��*wD7c8 ��v�`�ύcn�A�
"�q��h����1@k^&F �y�QXv�˭L?6{QYe�Ν6�Ny�r� �lL3�̀��s$�ު÷9�t�Ǳ! s��O�P?���Oc���(�f��v� ܕ�GU"��kzZ1t׎"@?�4��p�a$��A�~js���{<L g�xQ�_s;T gJ�ڟ@�?}�A� M� Ή�G�;4.�Gi͒_ sɠ\n��E�
@�"�r��cp�[� �:ֱ`%�	@�ӆ�T�S ϊ]�xf�0�R��� ��3JH& ���6�w|��f��D1x��?�KǕ�	��9�i8 n��f�G���A�͉2��5��j�Q�dt�M-7-)Mӣ�]G3%@��MG���!V��:�6 #.
��}%�LK��2H�oB�ݤ�:]�P����uk�IƄ�kw�x����(|X�RO��
�d�����h[g�E�u�w!$�w<FPC/V���o8 *W���W���\?�_	j�x����瘿D�`�`َYRI�W��:��K�	+��^1�;��*�v��Ë��rT�1�d���^@5a�����nfr��1�]Ŕ$ݫ^!��Z��x!��������`����tnɅ'.���\����q�d�]ؒ��ou3�(������ֈ�t�V���{�����Sl\mS]�\�p�q{�m�3<�w�ٌ5<�                                                    o�= |��,    IEND�B`�
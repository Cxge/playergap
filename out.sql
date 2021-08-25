PGDMP                         y           fantasy_football    13.3    13.3     �           0    0    ENCODING    ENCODING        SET client_encoding = 'UTF8';
                      false            �           0    0 
   STDSTRINGS 
   STDSTRINGS     (   SET standard_conforming_strings = 'on';
                      false            �           0    0 
   SEARCHPATH 
   SEARCHPATH     8   SELECT pg_catalog.set_config('search_path', '', false);
                      false            �           1262    16394    fantasy_football    DATABASE     m   CREATE DATABASE fantasy_football WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE = 'Spanish_Mexico.1252';
     DROP DATABASE fantasy_football;
                postgres    false            �            1259    24596    average_draft_position    TABLE     t  CREATE TABLE public.average_draft_position (
    id integer NOT NULL,
    season smallint,
    player character varying(255),
    "position" character varying(255),
    team character varying(255),
    scoring character varying(255),
    adp numeric(6,2),
    source_name character varying(255),
    source_update date,
    insert_timestamp timestamp without time zone
);
 *   DROP TABLE public.average_draft_position;
       public         heap    postgres    false            �            1259    24594    average_draft_position_id_seq    SEQUENCE     �   CREATE SEQUENCE public.average_draft_position_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 4   DROP SEQUENCE public.average_draft_position_id_seq;
       public          postgres    false    203            �           0    0    average_draft_position_id_seq    SEQUENCE OWNED BY     _   ALTER SEQUENCE public.average_draft_position_id_seq OWNED BY public.average_draft_position.id;
          public          postgres    false    202            �            1259    16395    projections    TABLE     �  CREATE TABLE public.projections (
    id integer NOT NULL,
    season smallint,
    player character varying(255),
    "position" character varying(255),
    team character varying(255),
    passing_comp numeric(7,2),
    passing_att numeric(7,2),
    passing_yard numeric(7,2),
    passing_td numeric(7,2),
    passing_int numeric(7,2),
    rushing_att numeric(7,2),
    rushing_yard numeric(7,2),
    rushing_td numeric(7,2),
    receiving_rec numeric(7,2),
    receiving_yard numeric(7,2),
    receiving_td numeric(7,2),
    source_name character varying(255),
    source_update date,
    insert_timestamp timestamp without time zone
);
    DROP TABLE public.projections;
       public         heap    postgres    false            �            1259    24576    projections_id_seq    SEQUENCE     �   ALTER TABLE public.projections ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.projections_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
            public          postgres    false    200            *           2604    24599    average_draft_position id    DEFAULT     �   ALTER TABLE ONLY public.average_draft_position ALTER COLUMN id SET DEFAULT nextval('public.average_draft_position_id_seq'::regclass);
 H   ALTER TABLE public.average_draft_position ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    203    202    203            �          0    24596    average_draft_position 
   TABLE DATA           �   COPY public.average_draft_position (id, season, player, "position", team, scoring, adp, source_name, source_update, insert_timestamp) FROM stdin;
    public          postgres    false    203   �       �          0    16395    projections 
   TABLE DATA             COPY public.projections (id, season, player, "position", team, passing_comp, passing_att, passing_yard, passing_td, passing_int, rushing_att, rushing_yard, rushing_td, receiving_rec, receiving_yard, receiving_td, source_name, source_update, insert_timestamp) FROM stdin;
    public          postgres    false    200   44       �           0    0    average_draft_position_id_seq    SEQUENCE SET     M   SELECT pg_catalog.setval('public.average_draft_position_id_seq', 648, true);
          public          postgres    false    202            �           0    0    projections_id_seq    SEQUENCE SET     B   SELECT pg_catalog.setval('public.projections_id_seq', 374, true);
          public          postgres    false    201            �      x���Ks�8ֆ��_�]��%^%�Ζ;�%�=��oK��1-f()���p;���z��.U��)���������I�~X��z���&�[.��K��>,N>ܷ�߾|y�����fǶ��m�{fM�`�r߰]۩��m2�M���g�M�Q���g'�ɴ�M�4�w]�|K���S���{�N����5?�M�h�7����cʿ�)4�TQn�;���������Rc.��o5o������N��Oo-�D��J����Y����j�^XJu��}�Լ7ֵ�����\�Y��,3?���t�޷�=������5��w/�uo��?�\Z��d��I��+�xel���������ǚX����b��M#_���	�c��S�~���7K.B J�!5A����䊉��ݗOO���� $�{T7��o��H���C�А��p�ٵ��M.��m���o��>�Lp��v*|߱u�.��׳�c������/bR�ׯ�j���OB<�	������'�V�߮x����?����4�yrW�O���6a0�	�'7'��-Y�"_��ũ#�N* Ʉ�kI:o��덚Yg��M �d3��ͪ����&a�N>�0�c����Y�C��q]����JKHVАخ�k�l�����q �)3��ZG�k���;0�S�$o�*�׫���^E��)����\%$������$9�ڟꩂԲB,�+��o�o�7Dt+����� �ͽ�<Y�΄vg3Ļ�'��;��Q������Hq���'7�nר��ё�	"5�)R��#����E��n��S�g�M���|#r2�����W���M�x��ثݲ}W+����-�	��E�t�ޟ%��q䐘��(qW7|�<��J�$��y!"��܄������ݾ��At��+�ۛ�C���Bl@��t�c �K>��s�C+W^����Oߩ��D��X�C]���g��"�bl��J��S����9d�S�`qw�C�mER�.��K�i{x����Rd����g�2����� ���[Y���˛�J_��(ѯ0�Bn䓧u�M����D,��	&�����~���A
H�R�aB�I*�_��|%��#ղ�]�,�h^@v��">�n�|k��V/�>	�L��oɗ�o��&��W��e��a���^t�p^��qW�A-�bW�͆�Cl	�%J �Z��v�L��.+sD,*M��c�[�ұ�*�!B�es���FD�������d�2�L�Г)�����%$�&F<�}�U�|�j���Oe1{�4���W���X�*?�-!����?ZY��V7M-K�*Iw!���+-t���]��,�kPu.!����J2o���Wx)�l��l��*�V�,�l�U��-��zZ�pq^��ŸH]֔j�TC<�	��V�bh����$Q�L�8���C����S�˅�
+��+%��v��뽷��
Ė��5�w��x����X+1�*�]��Jg��� kj�"޵m���p�⑦)��7��x��a+�
����ZL3L,v�޶MV	`S55���JΩ3�|[�w�
��v
Id��\�֬���1M!�ө�O�{"f�Jm�}J�X���e��<�����\���sQ!����J��Ut�
7��.S�(�9X��j*���1��&O�v3�\�u���)��2u�?Q��I��-X�Ӈn�\;$@�R�gw�5��<��ˋ|:Or�h	3"n��L�*��H)xoB� Ab�������d~9nق�(��ˤ"y|�wk�B`��T��"��3�K�f9�cU�+�w�Fd��~��y��"
�cM�Q,!�J\��⬀�=0n�W):Л*1$���Dd~3ڀ�"��߮�"� �9m?��{=�~{\��r�_~gS�И��ջ#*o���<��(��Wb$��N0�戅d����|�;{{��ge3�^gNG�����W����O�˼�(O-i�#�����(@ ��h�pPZ1��Rf�5T��S��X��s�<��=ozۜ9$���점��v#�NF/��!���In=��k�wL�/�Y�rx�NLĸ�oI'�W9 ��T�<9�w"P�1��gs��k�*��ê���Ɛ��)�C�E�D��S0J��a.(�?ޙ�K�LN�f��lR������{�=�U�呱�W2�dl��"IR����s�D�����w�0��O��ub���^��9�-�1��M
���*�ƾ����x�Q��!�HI�N���ѫˈ�+$�f�<L��;�����n���/��W�u4�i�&3���t����M��|��ͮ����y�&�ܞ��$bl#���I"�	��N<�Xm�R!������V�)s��{r[oV[M�31�)OJ��kvh�|j�j�`����MJ��;��w_o�K��U[|b�w3���?�N̸��,�\����b�x��e�(E�ʬr�v��5���m�"��IQ�7��@6�{n�l/��Μ����KI���޿������hbPA&i>������֝����!�!2���k��ղ���'��KR}�T!�;���$��bƇ�$g����mǃ/L���I3_�qɷ�RW3�Еa��N��fb��l2��VVV`�F�jC�n�V�y�ї�J"L������{rU�Á 7�01��@Y���wm��"n_ '�dD�V��2�ұ��a�1��$�o�:���� ^>����U�j�7�0��M���$=�'��8�ԼQ%� _4ȸ0�����Kg�@�AHBb��lN<�=rG��9��nF�}/ů���^)F���&T0��o���|��9��!B"�B��Q���z�l���O5�3�jC�x�^9��1
e��ES�G�k{���rs5-�;jWZ(�H0�rL���|�3[��� �ci��^���$w˛z+���8LM����}���^Y5�A�8��*��8�2͹R�n�fxP��ʥL+S#q�^��Ժ1'1������i�4�*�s�
C��k���|3��\8�������o^�-On�V>Y�*&�d����h̶[�����x$%��'�Ab��m�������T?�U�����`�.0�'�H��//�	ײ��bn�"�{� (O�=Ei���~m���m�vu]��%�t�hL�R�x�HF���m��@�luU�=tkI<W���HIR�o>tl��3d��� f"ɧ��A����f�(���k��=�^o�բ¼AI.������6f?�v
��I��'��obw����W�Bl�+'['��ϾTG� ���u���z��wm Ӹ ���#I�P�N7��.
��o��Z0��_��HR������_.[��(H:��OY�S�$��Ӭ�j�����Τ����9E��0wsR��.Dh����c!�;$5�x�Wd�6�l)@<��&�]"H��n�J$���6�G2_i�$��,�$�<���,���Wp��a�!��;�`Q+!�	R+C���/��F��0�oR�����|���3�^�k�զĜ��U��D"�M�gh�}`���	Q�� %s�u�.L�| q��������(E0��ҙ��,���M�nKb&�.���dB��ʽ�מ�C�)��ތk�H���ئ�ASߟͼ�v)��l�F���.�Qʗdm�7��4���R�K=�b�� ��¥���/v���O��� �$M�wkD������M��{�<���
�5�׭��NLp�t��� ��Ӟ%O�Ul7�ez��4��3A䬓�$�{'4(��4썋���נ幓�_+1�R���K����Ki	�H�`�m��*9���QuA�D��2���v�_�~��Ff�칓Α���b�QaF�U��l����
R��&6�+�S��5�X9��bw�K!O�=��]]�����M?TU3�>u�ׯ{��8~>WA�O2��>�0�Db`O���sY9#��=�����u+}2�]0�Ϟ����^=?�|F%
�3Ҫ^�Nޫ���\.�|�F9��H�JW��wb竪�A*RA�	V��Y�ov�u3(�VuMFzU%�7��@Oع��9@��S�����D.�9��
r    ?,#��9���R��H/�d/?� B�d��u��O��
�2�{�Z��.���>��?�w#CkG�����d���hU����^��LA@���Y�.�>�<�l��J�|EQ�g֊T��79
U�"�#�,8��;�3�08Bd��So�f˶ɢޅ���6�^g6�ڞ3�z�{k���q�^�y���7c��o�3L5<�l����b͋~8���I���d֕t�oI��������=b]!q�%��A\2R���-��D^�L��[D��9Y�Л�C!�*Ҥ���-"zɬA���ݒ�OE�c�.Z���IR��w��#q��z�'A��1O|��1OE�Q�zG��e�L��;&a#]�1yǄ�2��L�R��
{��\w�dD6鈘�;&��.5f�� ��h��u@N�3ҥ�,�S�(��;�++z�����σ��S�10�w$��Jfũ� �����v����ca�K{�o��c���1�yǂ\��J{�������F��]v��A�Ԩy��aj��I��;T�y��v鎆IA�5fl������ǩ���� '��QG���Y"Ej̝ݱf�RDe�Cz��>��^��[T�^�H��z�q��CCsG��T��P`4�XqPFZԡ��#ajڤC���,D�%j����a�8� �L�
�tL�CH�'��aJΤ?��
�Q��L
�Xǂ8�eSkd8�7w�=��0�O����r��u����0���5f��`9�3���20��Y�HO�Ӹ-��ar)��FM�Sϙ��Y�.��̬�4�
�`��cf��=3|�Q�4�K��!���j���gG�ݩ�?#�i̢ޱ2H�����$���~�����I>Hvo(�h�ln���3�Hp�uw�9�#�=���ջ�+��0)N��|b�9�$�LÇ!3I�;hF�+����Gr�|rԄ�� HN�Ӂ	�A6J9iM��I<����I��ȴ�7�q ���$�1�p8�/���Y7�jeN"ӈ#�Ca�~N\/��'��a�q��t���A.B�U�E� 8�����t�w��a�4	M���;$DŒ[��ׁOB��4���n����=���:p�f<:qX���ANvr���F��Y�f��w
ȵ�<����y���r�ƍ�r��?ǌ�
r*���4�8�X�~|yf���F8�;2IK#��ٌ��54�w,L��A���O�A��!�����'�0#��>��fN�>h"�� �Vy�:[�\�=���4b��0����h/�)��$7o�!!�<?f��K	O�=�<�(+w��~'� ���:=�z�cb��OG��"�䶽T�|��b��ƕH���I��c�� jޜ���]$b��X7���A�%rR���=ĥ /�E�X� ��ɉH�z��?`"�&)R��
�4�G<�=&��(5��`�T�C��~@BgR�F�m=�9)�~�� ��_�z��QN�Ԩ'q@C�J{�3��p��iSc���ld�T�� �?yy����Xh䥭��:�x8�ipN՘�x C�q$P=���]8��T��X,D�$�j���G����I�o�� ���'a_��YH�o_�� ����&+�B�I���X�OfB��O���O��l�.�H��x�	<�Ē����ì$a��_0ĚJֈmv���ǰD���h�x>5ha�	<�D��uv@��4Ibv�S�$	�Q~��]���h���9���Aoi���5n���0�ę=݉�4DH!U������$n�y�0D��]�B�_���Ϥm��(D)�d�QS~G+!��k�3x�)G��X�YH�:�(�!1EY�����{<�����1�� �X棾�
1.���'�U���P5Ex��Ig�Q�� ��UH�z�٭��G���  g�xsһF}���_yi� _� ��5{k���L�p"@v=)_#��,JP�?<�� 창B��|2�G�=D�R�
v�?<��[A*؈�`��L6J"]� W(H;֚�B$6�`�Ry�����' (ms�&�1�H��h�@���ö}��Y_{g���\���,���?��#q�|9k,H	;� !���{<P��]�tܵ�cA����4�
H��f�V�]S<^��q��#���K$�v*�P�j���W�G��L
Ŏ7�	��E.�=h����8��5?�"�~�aZ^a��̆�A�怅H�H7e�pilA�؞=��L!'��U�r�W���7��m�R�)H;ޫ�4�$��$�!��:�E���4�ckY��Q�VvK��8\㦐�����ڐy4��� Y���	�d����*H\v�؁gz�B|:RĎ�����D�Q�t�7�g��Fx4�6����h�ǛA���Ď���d"�0V_Iz�b�t�������*����A���a�9�-�c��9v(
k�8���L&���A�m${�y�K
f{Arס��d@��V�:tc�L�M�֡g���yY%E՘��� �Q�ݘ���@^ڨû֥c f��,е�dH���GӐ�Lb�~CBd|�T=��"�Y'ո��� C�ԩ����� �Be��;��%R1�&�}|Řc��S"�j��D��?�홨+�� 	j܅ހ ��/��
r�� �i��^a0�2�����|�����+���.eC�r��|�#��
�9���=�z��
�|/�G}��6��4⊮rjLb�P��+&L��+&�l�� �;H�DG�H%:�uW�����1/m��d!3[���+fKBBЁ��d��X�n:�o7ȇ!s����`�:���9�+�p;�Q7�+#�gĸZQ0%w}����/�s�(F�F*�GlE�h����x�o(�`o����r� �f�g^� �	6c��
,$Ԍ8�
d���{Nކxi����@L)J�c�m�J�b�L��o�V�9⣭Pߞ��C�i��rʉ=A�5�0 ��)��2b��0�H9�7V#v�<9�(]S�H��,>%�,c.�
�
ʴ�LX�+$/(IX5�VH5�$Ee܇[� F�%�)��Ↄ��J4�-@� ��J�#1�W���Lm�`ອ(�ҒԒq_{�t�,I-�:V�U���t�q�p��AK�I��1�̟���
q�+m#�h��T	J�~>�Ư8�%�t�q�]��Kg��+������c�ֆ���a$�l@G��ձ2d�PfN3��+�,Y��1҅�P����c��
�ٍ���۸�a�
��Ѹ� �)]Pl/=Oψ/�AJ-e�����+�l�̭C��}�P .����*�f7�4�C�y �8j#n@��@��1;e���|H�8��P�s���=��T(f�P������`�֓s��m ��VX)��r]Q ���b�?J�O�0�VIjÈ��� ���#Dln�DS� �a��0��Crè/*���5،��k�n]Y���#�AD�ei���5�	-I�x��p��Pڰ��� �V��횣����<UN暂�A$F��jm%ā�$9�s9����G-���X\+&"��B���f1�ZM��SH�8�UN4�$Q��7�(�e�d�����Y�81bM�1��Be����)���/I�s�%�+�41��0��D�ā'��@�%Ic��ѓ��K�(B!&$�<�5S�%Yb�Ǔ8���׎�����e{�a�Fa�H$Q��8k�f�;z��5	�N+I�u0'b%'�bܲJ��p��5��-I�x6j �/�`v3�;�2�ȥ�r����<���$� )�M#4�[ΎZ�	��Lh����I��F� Lm�ԋQ�z�k�!e����{�ah�H(Ċ4?j��H&M%%�Q�e"f/)��DBD󹳍�Q� �F�T���ā�:%b�ܚ��W�T,��A�Q�&�~�D��d�Gm�	��	cf���D��N�	�u���4��u5�	�m�4b�TMF��Xo+�8 �  �������9� ����G~h$�V$t<b�N8İ#����AJ�~}A�qR<��ȉ�D��x��!kd+S��1濯9�|�
,"C�}���q�t�[C�q�v$�T�1�v� >����8�Daa�}�X���/!5��g��g�%��0��&
"~�2ꨯA�͊���&�D��(#�L�5"�2���{�")$��'b$]d�\�0���4�q{N"!ynk�w�f@��!���D�|�(�O%y�
l)��k�-���CDq�E��'2��Z���Ba�jU�mx10��H���p*�]��؟�4�go��&GI"�v���$���T�)�@�*lǭA���Q*�E��5	�	+l+И�-�+D�SA�LB5
�{�"�d�lUc �������/��Eq6      �      x��]Kw�8�^{~w�J���f��W{dw�Μ��%�b�"=$���/��"`%����F���o���ޅ� E����b�nĢ^���_GW��x�y4:H�G2�c�s�?s���S�C��~��=�s�1_�i4�N�?Fa�������Q&q��\��"8,KYiG��yf�.�82�'�34��_%Iރ���L�m+�2�Z�mm�ܟē�eps>�������o�|�`@s�)eܬ�F��
��􋺣�D
w36Т�b	#��pOG��k�Mp)fK<����h2�k0��I�\Tl��8��М�ep��vVw�s��ē��I��pM����L�ƒ�C��U0��ϲ1�t~���)J�Nb���#=�TiP�UpԈ��cb�?�dp$q�|7܏�M8��	j���*��ͣl��\*z�Q�@tcԖ�s?�+�,����#�#��3�sw�� �Acs`�8�o�#eJ��E�q0!R�FT���*�(������A��%pQ�����E!)����$�aϽ28RS�j$�_n��[��F���!����� �^�28��mQ�k����D&�c	��Pd�W`R��A�]����}'���f2<�A�����B����1��C#��Mp-^Yͤ�s�U*8@#J��u��1%C��q3{>�ec����!����8b�U��tSȾ'��JnDӘ;�� NC��8Rq��*���{�
NDSե��c--�M)���	jζ�Fpx{��	�Ǫ�epYW������ �OA.�,�Y��bǓ}�wH�Gb���yR��l�O��W����*���=	L�|$���ݢ,Ze���6F�˃Ҧ�e�������U;��pVt�_�)�h��+�w&�� 8�m��h_�D���@=��DQ������PJ|�m8�o�{������q�o�}y���Bh�
���F*�r�"�aE3
F�UV�w����v߸Q� � ����ȭi�<8����|��"�>q7�'��K{��('$+Y�꒪��[�]>��,�荋[0!���1]�*������ ̑e#P����Sޫ��p 	?��|���B���9Q��H�OxB'��
T����z/b�|t ���ɀ��_5��Bk`>�=A~�4�\�̦�ͩ\���:�Z���,��ٞ�(F�=��-����XGE6I#����~,A��{Y�V��\��//uY�MP$�G�9y�̂^�ñ�����A�#�sZ��|����3Iɽkb�(Wth ���	:/f����ɾ.���3�Ǵ$,��(x����W³'���s��*ڿ� Rn�6 #���K3LZ�-}��I�����Mn!�	r\C�d�KL(� f�cp*PF�]�
!�Γ�����"�I>�Q'�ЂYTʑ�֓3��u��8�g��AB[���zSJr 3���f=����AD��=��z^�/����,��YJ�Y>��)����g���/e?`���}IEbs,g���j�>ab}�S?�b6��Q㋴������!(��"m9��>��O4�u�b���;�;�F�6�ӀhcOl���Z/�E�K7�:��h�E����
�Λ��-t��Y?�rC��N4����
���B�mU��RDQ����IBSJ4��+���@:	G����]Y�
�M�{5J?��̵�,�o�j�
�p y����r	��� QH�%�=��I@�
����B��G񾳷	�,b&���}ݔrC���*b%��ɞj���� �jTИ����=`�(�U����+ʢ�3ex���.r:e@�BT�>��ӓ
'�`U��&L�o�HG���=��)S�V��(���.��UY�H����ҧ\�o*68�����A�EG�y`��ge������Z�����] H�c�^Ȉ�_dc[��Tz�].u��,]����/'�B $N+e	����Zٖ#�,KYMe�Cg9�z(	��P(�W��M�"�)ظ�Q`2&�֏�	E�V�[�B�I�L!dPb���w�/���j�����0�4;ʝ�$$�}3偺�*je�[����S��8���\$H���Ҏ��G#$��P`{2
�%��Si�ā�z+��2�P>Qa�FGp�#�Hi�@	s� �B��t)Ki�U[��I*&9	Ķ�Yh���#� P�8tw��'2	�_���ɑ\���\��W���OR���Ԁ��%A�;�yn��,��q[�L�iEu�W�<  ��	S^�L�b��U�\�$8:C7�Nx�~�(�bA�=����72�-����(O��1� �� ��s
�?_}N��G�V1�y ���IfE�M��9r^�}:_��� ��l:"&�@{A�l��H�D5ZT �ÐO2��J�G����UЫ�Ʀ�z�8��kl�x���g An�����b]u;�M��&S�63�t��h��yLk-������ie��R��؜�8�1r��F�̹h�E�� ǇV��eAN�p��9�?B7��-h�gC�b�2[��l�R�=�6�NQ� K*���P��q^��&@bp3\+3&N5���wD�������&��U�AN����u9�N�LM��} ���Y`G �C�m��B�6�.���B�v!��@��f;=a���o��JݥQbՂ��mB��<t���Yq���ZtJLt���wE�X�^��x㈋����62�iW���NJ��H��;�@^�!��u�½rnc���+D۟��L�b2!f-f!K�?w���f�!�H"�> y�ܫ� ��+�@�y�O�baM�������Z�{i��Y�n*�ur�݀#��L:R�9*�K�6:��9p���ylC,�2���6�KU+!�-*r�!�F
�v<1�H��&���
��!���/ؖ����L��_W��.K%*;�h!V7Ƕ��:ö5$�+Y�NœF,� �3RW>�6ƶn�	���kG�V���#�)Lǖ��΄G8"������fvU�m1ۙ.� =�t�`{';9��VO�����z.e' ��QXcki03�rU&!�>HȂ�r%��c�v��#	�؄#d�C]�?Q4�;�W��Y��n�4~@L�Xo7Y�>���yV�q#�0�s�� ���q��%�.T�~Ѱ����-P�/d�I�P��R�*կ�cQg��,�_�| �K&_��!�9E�j�IBn4�( %���
�vJH)	�9-�y�>ʲ��o���tG�1�`!+aY�i(r��8phjc�L�ݎ�إz6��3[�]1�#�ٙ����8�������X��^�,w{#���cND_�jk\�ki��xH��c[�����H�Z�G�WJZ��f8/1�쁀�DlԢjr$ou(��s��p|���
i*�A4���[�j��`��&2q�d�C�zظI�A ��0>ꉄ}o�NJ����́�/V��ڪ۫�$֣Z�E�3���z3�vN="��� �yQUɦ�`b(ڤ�'���W�ub}� �b#5M��"�~b'��8[wi��H3zp_)2�Y�Ęjd�wۍ7� �IUn:hOx9�$@q�m��0�Nu�Y��G����1g�An�#�,���,���8=���1��Uzd|�Vp�%M螱��잢����@)�����rg��сy2���B;Q��6���w�1�p9�Bd_	�t�[碨^I_-�X$�y�Ń���J�%�?� ���<o��3���h�JE��K�܈�΀�o8��wW��t��b%�;�9�g;m����i�����K˺���o��>|dL�fν@?%�W��lK�OO}�l0��iS'{����ntkSp����I4���okiz�D�KaF�J���������)�{�$LN�J��nϷ����٩����.8jd1;�u���9
�/lJ����bc����uC�Q�6<��aG�45uXu��Δ��|w�ٶn`>�Me46��֬Ś]��}WG��Z ��*�8�����9(�C�K�+N���� l�:�����G�u    �D!�N5�ٜ�a��hsD���٩Õ�Mp�8_+�Z�L�Eۑ�i�F��hʕV�[���n"��qb����ϩ|~.��^U�	�� �>��X�u��-�;�	d%s+ �l�����N�J����n��N�)�q�����ep�*����n��ek�/b��3>e��y�Í��-� w���iU*��K���k�F��Ċ����/�>O��5yկB+n�B�д�u�r��OD[Ե���z��ʚ=,��K�ۨ�4L�ul7#���w��e�p�#,����7YoU6��e���E�SGk��D�'j�`��}���d�i1����u^ʝ�N�8�N�4,5��n�X�b�%K��c�@�R�z���3݅+vwޤ?����zب�_���u:����K�o�Ѡ�3���6��Gx8�j��y�?����ξ._D�0�7-�ĥpv��r��O��e'�|qs�����D��a�8���Y��Y|���a��~Y�)} C�E[��88H�;�;�\��x~60�{��7�K|a��B�w�A�k�c�w3I�H�f��\��Ba�����Y�剁��L�<���U���`��%�4���mP(�I?�'|?v�r��W�)����I��WK�#�SC�X0��I��
��1<�l�պ[$M �g����;ҡp��u��9=��n�Z/Q�����j�^g�u"�p��Z�/*ϛ}�zY����������$�� T6�N$\�uS�{�7n�Jij��⠪�Q��j���Z�-�.{���c�(�A��<�2��ǝ�iF��d쳠�'����+܈����mKh������9���B���%2�Q��+�YG�w�����3z>�n@%)DL��n:����]�5�o#A���Г��7u�HsCJ�Ε��[6B�w:)����\
�`~2��e��0_M�>�Um��������1�_چ�$d��KHeQcߙ����ɘ���A/��~��-�zm�lS9��A�Nfy.?1'2�KxGL!�S;����	iR�W]@:���H��4��x�����O��A#N4l��{뗝�mHΦ/�q��z����<C7H���.��'�������up/VkY����N�O�(��I4�]���`�y�g&s���/[JR�\�7�v-�dE���O����k�m�-����K~To�޾EƇ@%$m�W4F={�~~
iĄ�z�S�f8.�楮K_3���+"dz����:������Q@N'�wD�K׺����BVb]v;��©���,J���C�Ta<��>�KFb�|1P#�ht��Z�x��	`?��X(�7�.�&��Α��Pc���OH���=�ǖt����xf�p�~��h��/î�i$c�3�z�G����]�GE�X��t�;E��{�������hN�(��v?7�i�ҏ+�?u���$M��.H��i�Fa���u��z�P9�7hR�V��:���E���i!�u� ��n�hT�F�We5�
���,b�@
�w�����́��,���@�~�`�Ʋ�P3�6���U%���Щ�
�jë�UXӍ_Oi���$GR�X��)!�zd1���JQ�"�~�'z���G�hR�g�i��h�)��Ք����s�,wV[���I���i*i獄��O}o�(������V���ˎoW�lٌ��'�>�^E���؀(��>��D���{p���_1��q��L��ҏ#��uWt���	$~��9��@ց�#I]O�*�]�ג���t }���_ba�>Q	�Ч�}����,)����q���D>���N6eQ=�P�E���j
�g�F"M�S�s�~������v5�8�?��B���U�������%�z5+ƅl����BC�(!�����'�%��A2=��ނ�G�>VףG|	���^�����ꣷ��'�F_���Ju-{x�Y8��mYhIŬ��~P���|��1>���1$����Fn����b�����������a��o} a|���J�~�f����g��Qw�ő�Ux�~�x��nw�㋳Q��A$�Ny*7�-Y�
#�f�֓�/�7���h��@g�OA_9���"M���28�=�B�0B����8-*k�<L	=C����s�&��'��W��a}_�Doz���wtx<��𽿤/��)��l(!�S���yһ�f{�"/�mu���S��rE�f���L�U�AHzYB!s(�J�?�R�Q_�y��ǋ��E9��im�e�I�]��}h]}���s�s}�h�F��bQ�Sg������$�>�
(��)��F>+E����PW�Wҿ�d^n�+L��t�s��3�ۗd)`;��NO��%��ٺ|�6?�� ��>��v����Z�巾0|:;�|aL�R��XwRzK(�q�(�+G�Hq����2mvꨳR�=>k� ҕ΀^����<��Ȝwf�yp,V/�\N�6 �qP=�$�M��h���(�A�/�(t�m���{!}�`�\� ����B�L0�ᬈ��~/�c�n���(�Ǡ$������̙�P��u�ܫ�T����p�r��o�?�]�7�}'0�5b� �����1�=���	�4�	$1����7���,�rɷ&�}6d܉v&��΂�l��ѭ��U^N��/�� ؎�=l�]��-�f���//Dy�~�y_��Q��i�!��`L�F4z���W���u�Pu֕�@��������1�'��qMA=k�|^�'����
H��dѻF���nˎOe��#~j�F�n���4���t�����b�W�Ί����tp���D����B3H�].y��E�
W�B�s�����P*R�.߈Ə����z�,����A�?
��*�GW�'�� "��hl}�U1��2����ַM�S����SjIOOk�o5�+�����Gc�����~b��F=����y,!�����gȅ΃����.���˗�ڻ���0����� ���~~�����F�J��=��p��=����u�a	���������Le���^~��\���hx"9[ei��zSU��_�`hY��L�ΐ�9���Ao�},�DƿrB7��mZ�˞@Wj�v�ߎ9�G�_z��F�Ii�*��8�u��,t�����G?�܏J����]����`��.�V{>�)��0�J�Q���Bo�h[��f���WL#G�!GeM���1�6�/	�Q��)���^��kI�Ii�.Řƍ�,VE��պ��<��n��nT�G�t�Zs%˙T��'���E�~|A�Ϧ1��&�Px�?�B�0
�c�1��˺y��U�u�9�
3.M�s�1�����zm5��(C�����i�ȼ�;���5!��{v�H�����Q����ތH�@��iJVz��!mË.`�h̝Ԍi�7��A���s���٘挮�gQ�s�0�86��\ƞ��C��s�*߷� |2Y�`�}������P�N�Ԡο���༩�e���Ax8x8B1��h�4et[�Ep&����%�C�1����༖s�P����l����0h��R4rn�� S����]���R��N���Ƿ���c�q�{�U����3��o��!�:���f#��J���|q�n$���O��F/bӞ�G�G!3��/Z,�=gE�l���I�q���@�<m�Yp�؀�������f����pXÌ���&``�/�4TtK=/`y��S�JƎP�NӔoO��/YR�"wz'�q"�[~h�#�$"�Ò�}��ȩ�������1��q��c!:���ߕCe��'[��( � ��|�N�D<>�|���x���M���t\����G��@�4C�'Eۖ_��)�8�N����E�UQ]Up^�\�6�nĊcwz�j%����<�S�#���e����� Oƫ��Ξ[�i`��n���k_��&��fXH��F�7��כ�P �oG�4*t!6�F|�n��7�}��.�2��c���y5�A����<Әй���L7��ח�G�P�0О��� ^  ��hP=|�l��uԎ
�T z���^HO��>��Ӵ�1�������m��iX�z��~�?`�,B_-��o�ޣu�gy>�H����yX����׵|~\W �^M���)�NhR�D���b]����tҰ����m�&��'�iX�D;ۍ�4�̻/��S��)�+e̕_�U7)VϾN?�;��1M	}y���:	|�Ȝg�&��n�X��:���������z^�/�d���0Ӝ�I#_�z�`N�R=�g?fc��\G����[y<���]��!pn���������q��@#B�b%u7�Q�{�L)>e0�6-�����NtO��x���2r�~f=Y�R����{��$��5f˞b�B��&=�(�0��}�m<+�(�)��i,�8W
�.w癤�ƍ��S4t':�xV!����>L��a���4t#����6���E�Yxs�ś���S��~^T�m7�~v��{�b�Ի#���J9�����	���h:F/yn��/ A德Ӏ�������-ϒ9��e���%��z�O6*��V+��k���]����4ʖ�~6��I,d����^��}z�?����?��n�     
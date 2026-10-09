# Trait taxonomy for AI personas

Contents:
1. Tiers and what they allow
2. Selection keys with observed values (39 presets)
3. Full option catalog with tier availability
4. How presets combine traits (patterns)
5. Reading the table for a new persona

Source: the 39 example presets (each has a tier, a seed, a `selection` object of trait ids and a casting `brief`) plus the option catalog that defines labels, maximum picks and tier availability. Trait ids are internal codes; the labels are what a person would write. For any generator you simply translate the labels into prose (the codes matter only if you drive a tool that takes them).

## 1. Tiers

| Tier | Meaning | Presets observed |
|---|---|---|
| normal | an ordinary believable person; the smallest option set (no exaggerated tiny head, neck, nose, ear or teeth options) | 1 |
| freak | an odd-looking but photoreal person, deadpan art-house or fashion-editorial casting; adds exaggerated features (long neck, unibrow, jug ears, gap teeth, pointy nose, weak chin, big forehead, tiny head, high forehead) | 17 |
| total | the same as freak plus the most extreme anatomy: caveman skull, gigachad jaw, mega jaw, centaur body; briefs for this tier say EXTREME hypertrophied / extreme exaggerated anatomy | 21 |
| insects, frogs, cats, dogs, capybaras, birds | animal tiers; they share only the options marked 'all 9 tiers' plus the freak/total options marked 'FTA' (hairstyle names, facial hair styles, egg body); no example presets in the source | 0 |

Tier code legend used below: `A` = all 9 tiers (human + animal); `NFT` = normal, freak, total; `FT` = freak, total; `T` = total only; `FTA` = freak, total + animal tiers; `TA` = total + animal tiers.

## 2. Selection keys and observed values

`Max` is the maximum number of picks for the key. `In presets` is how many of the 39 presets list the key at all (some presets list only a few keys, and `distinctive` is often an empty list). The count in brackets is how many presets use the value.

| Key | Label | Max | In presets | Observed values (count) |
|---|---|---|---|---|
| `gender` | Gender | 1 | 39 | Male `male` (24), Female `female` (9), Trans man `trans_man` (3), Trans woman `trans_woman` (2), Non-binary `non_binary` (1) |
| `body_type` | Build | 1 | 39 | Slim `body_slim` (18), Athletic `body_athletic` (7), Heavy `body_heavy` (5), Ultra Muscular `body_ultra` (4), Muscular `body_muscular` (4), Curvy `body_curvy` (1) |
| `hair` | Hairstyle | 1 | 38 | Bob `hs_lampshade` (5), Bowl cut `hair_bowl` (4), Perm `hs_dome` (4), Mullet `hair_mullet` (4), Volume waves `hs_pompadour` (4), Long hair `hair_long` (3), Side tufts `hs_tufts` (2), Hair horns `hs_horns` (2), Pigtails `hair_pigtails` (2), Beehive `hs_beehive` (2), Hair wings `hs_wings` (2), Buzz cut `hair_buzz` (1), Bald `hair_bald` (1), Curl sphere `hs_sphere` (1), Corkscrews `hs_corkscrews` (1) |
| `hair_colour` | Hair Color | 1 | 38 | Jet black `hc_black` (10), Platinum `hc_platinum` (9), White `hc_white` (6), Grey `hc_grey` (3), Chestnut `hc_chestnut` (2), Pastel pink `hc_pink` (2), Ginger `hc_ginger` (2), Lilac `hc_lilac` (1), Green `hc_green` (1), Dark brown `hc_darkbrown` (1), Blonde `hc_blonde` (1) |
| `aesthetic` | Style | 1 | 39 | Retro `retro` (14), Sporty `sporty` (5), Streetstyle `streetstyle` (5), Y2K `y2k` (5), Goth `goth` (4), Theatre `theatrical` (3), Casual `casual` (2), Suits `suits` (1) |
| `ethnicity_origin_base` | Ethnicity | 1 | 36 | European `european` (12), African `african` (10), Middle Eastern `middle_eastern` (6), Asian `east_asian` (4), Mixed `latin_american` (3), Indian `indian` (1) |
| `age` | Age | 1 | 38 | Adult `adult` (20), Senior `senior` (12), Mature `mature` (6) |
| `skin_tone` | Skin color | 1 | 36 | Deep brown `st_deep` (7), Fair `st_fair` (7), Olive `st_olive` (6), Porcelain `st_porcelain` (5), Tan `st_tan` (5), Light `st_light` (3), Brown `st_brown` (2), Ebony `st_ebony` (1) |
| `height` | Height | 1 | 36 | Tall `h_tall` (16), Very tall `h_very_tall` (13), Average `h_average` (7) |
| `proportions` | Proportions | 2 | 35 (empty list in 7) | Broad shoulders `pr_shoulders` (11), Long limbs `pr_longlimbs` (11), Short legs `pr_shortlegs` (4), Tiny waist `pr_waist` (4) |
| `freak_head` | Head shape | 1 | 36 | Standard `head_oval` (8), Long `head_long` (7), Gigachad `head_herojaw` (4), Tiny `head_tiny` (3), Caveman `head_ancient` (3), Mega jaw `head_megachin` (3), Round `head_round` (2), Square `head_square` (2), High forehead `head_forehead` (2), Heart `head_heart` (2) |
| `freak_neck` | Neck | 1 | 34 | Long `neck_long` (14), Column `neck_column` (8), Standard `neck_normal` (7), Short `neck_short` (5) |
| `eye_shape` | Eye shape | 1 | 34 | Hooded `es_hooded` (10), Almond `es_almond` (9), Close-set `es_close` (5), Upturned `es_upturned` (3), Monolid `es_monolid` (2), Downturned `es_downturned` (2), Large `es_large` (2), Uneven `es_uneven` (1) |
| `eye_color` | Eye color | 1 | 34 | Brown `eye_brown` (12), Blue `eye_blue` (8), Grey `eye_grey` (4), Ice blue `eye_ice_blue` (3), Black `eye_black` (3), Hazel `eye_hazel` (3), Amber `eye_amber` (1) |
| `freak_face` | Features | 4 | 36 | Thin high brows `ff_brows_6` (6), Pointy nose `ff_nose_2` (5), High cheekbones `fn_cheekbones` (4), Gap teeth `ff_teeth_10` (4), Heavy eye bags `fn_eyebags` (4), Unibrow `ff_brows_5` (4), Freckles `fn_freckles` (3), Thick brows `fn_thickbrows` (2), Pouty lips `ff_lips_3` (2), Dimples `fn_dimples` (1), Uneven ears `ff_ears_9` (1), Jug ears `ff_ears_8` (1), Beauty mark `fn_mole` (1), Brush brows `ff_brows_7` (1), Full lips `fn_fulllips` (1), Wide mouth `fn_widemouth` (1), Weak chin `ff_chin_13` (1), Big forehead `ff_forehead_14` (1) |
| `facial_hair` | Facial hair | 1 | 37 | Clean `fh_none` (16), Push-broom `fh_pushbroom` (6), Pencil `fh_pencil` (6), Moustache `fh_moustache` (4), Stubble `fh_stubble` (4), Braided `fh_braid` (1) |
| `distinctive` | Distinctive features | 2 | 34 (empty list in 17) | Ear piercing `df_ears` (4), Odd eyes `df_hetero` (3), Big lashes `df_lashes` (3), Brow scar `df_scar` (2), Piercing `df_septum` (2), Bleached `df_bleached` (1), No brows `df_nobrows` (1), Gold grill `df_grill` (1), Face gems `df_gems` (1) |
| `accessory` | Accessories | 3 | 37 | None `acc_none` (17), Jewelry `acc_jewelry` (10), Glasses `acc_glasses` (8), Hat `acc_hat` (3), Headphones `acc_headphones` (1) |

## 3. Full option catalog

Every selectable value per key, with the tiers where it is allowed. Where an option carries a slot tag (Features key), pick at most one per slot to avoid conflicting features (inferred from the tag, not stated in the source).

### `gender` (Gender, max 1)

Female (`female`, A); Male (`male`, A); Trans man (`trans_man`, A); Trans woman (`trans_woman`, A); Non-binary (`non_binary`, A)

### `body_type` (Build, max 1)

Slim (`body_slim`, A); Athletic (`body_athletic`, A); Muscular (`body_muscular`, A); Curvy (`body_curvy`, A); Heavy (`body_heavy`, A); Ultra Muscular (`body_ultra`, A); Centaur (`pr_centaur`, TA)

### `hair` (Hairstyle, max 1)

Bob (`hs_lampshade`, FTA); Bald (`hair_bald`, A); Buzz cut (`hair_buzz`, A); Bowl cut (`hair_bowl`, A); Mullet (`hair_mullet`, A); Braids (`hair_braids`, A); Pigtails (`hair_pigtails`, A); Afro (`hair_afro`, A); Mohawk (`hair_punk`, A); Volume waves (`hs_pompadour`, FTA); Beehive (`hs_beehive`, FTA); Perm (`hs_dome`, FTA); Long hair (`hair_long`, A); Short hair (`hair_short`, A); Hair horns (`hs_horns`, FTA); Soft-serve swirl (`hs_softserve`, FTA); Curl sphere (`hs_sphere`, FTA); Mouse-ear puffs (`hs_mouse`, FTA); Hair wings (`hs_wings`, FTA); Hedgehog spikes (`hs_hedgehog`, FTA); Side tufts (`hs_tufts`, FTA); Stair steps (`hs_stairs`, FTA); Shelf bob (`hs_shelf`, FTA); Corkscrews (`hs_corkscrews`, FTA); Side coil (`hs_sidecoil`, FTA); Mushroom (`hs_mushroom`, FTA)

### `hair_colour` (Hair Color, max 1)

Jet black (`hc_black`, A); Dark brown (`hc_darkbrown`, A); Chestnut (`hc_chestnut`, A); Ginger (`hc_ginger`, A); Red (`hc_red`, A); Blonde (`hc_blonde`, A); Platinum (`hc_platinum`, A); Grey (`hc_grey`, A); White (`hc_white`, A); Pastel pink (`hc_pink`, A); Lilac (`hc_lilac`, A); Blue (`hc_blue`, A); Green (`hc_green`, A)

### `aesthetic` (Style, max 1)

Retro (`retro`, A); Sporty (`sporty`, A); Y2K (`y2k`, A); Theatre (`theatrical`, A); Goth (`goth`, A); Suits (`suits`, A); Streetstyle (`streetstyle`, A); Casual (`casual`, A)

### `ethnicity_origin_base` (Ethnicity, max 1)

African (`african`, NFT); Asian (`east_asian`, NFT); European (`european`, NFT); Indian (`indian`, NFT); Middle Eastern (`middle_eastern`, NFT); Mixed (`latin_american`, NFT)

### `age` (Age, max 1)

Adult (`adult`, NFT); Mature (`mature`, NFT); Senior (`senior`, NFT)

### `skin_tone` (Skin color, max 1)

Porcelain (`st_porcelain`, NFT); Fair (`st_fair`, NFT); Light (`st_light`, NFT); Olive (`st_olive`, NFT); Tan (`st_tan`, NFT); Brown (`st_brown`, NFT); Deep brown (`st_deep`, NFT); Ebony (`st_ebony`, NFT)

### `height` (Height, max 1)

Average (`h_average`, A); Tall (`h_tall`, A); Very tall (`h_very_tall`, A)

### `proportions` (Proportions, max 2)

Long limbs (`pr_longlimbs`, A); Short legs (`pr_shortlegs`, A); Broad shoulders (`pr_shoulders`, A); Tiny waist (`pr_waist`, A); Egg body (`pr_egg`, FTA)

### `freak_head` (Head shape, max 1)

Standard (`head_oval`, NFT); Long (`head_long`, NFT); Tiny (`head_tiny`, FT); High forehead (`head_forehead`, FT); Caveman (`head_ancient`, T); Gigachad (`head_herojaw`, T); Mega jaw (`head_megachin`, T); Round (`head_round`, NFT); Square (`head_square`, NFT); Heart (`head_heart`, NFT)

### `freak_neck` (Neck, max 1)

Standard (`neck_normal`, NFT); Column (`neck_column`, FT); Long (`neck_long`, FT); Short (`neck_short`, NFT)

### `eye_shape` (Eye shape, max 1)

Almond (`es_almond`, NFT); Round (`es_round`, NFT); Monolid (`es_monolid`, NFT); Close-set (`es_close`, FT); Wide-set (`es_wide`, FT); Uneven (`es_uneven`, FT); Large (`es_large`, NFT); Huge (`es_huge`, FT); Hooded (`es_hooded`, NFT); Upturned (`es_upturned`, NFT); Downturned (`es_downturned`, NFT)

### `eye_color` (Eye color, max 1)

Black (`eye_black`, NFT); Brown (`eye_brown`, NFT); Hazel (`eye_hazel`, NFT); Green (`eye_green`, NFT); Blue (`eye_blue`, NFT); Ice blue (`eye_ice_blue`, NFT); Amber (`eye_amber`, NFT); Grey (`eye_grey`, NFT)

### `freak_face` (Features, max 4)

Freckles (`fn_freckles`, NFT) slot:marks; Dimples (`fn_dimples`, NFT) slot:cheeks; Heavy eye bags (`fn_eyebags`, NFT) slot:eyes; Blush (`ff_marks_12`, FT) slot:marks; High cheekbones (`fn_cheekbones`, NFT) slot:cheeks; Full lips (`fn_fulllips`, NFT) slot:lips; Thick brows (`fn_thickbrows`, NFT) slot:brows; Beauty mark (`fn_mole`, NFT) slot:marks; Potato nose (`ff_nose_0`, FT) slot:nose; Button nose (`ff_nose_1`, FT) slot:nose; Pointy nose (`ff_nose_2`, FT) slot:nose; Tiny nose (`fn_tinynose`, NFT) slot:nose; Pouty lips (`ff_lips_3`, FT) slot:lips; Tiny pursed mouth (`ff_lips_4`, FT) slot:lips; Wide mouth (`fn_widemouth`, NFT) slot:lips; Unibrow (`ff_brows_5`, FT) slot:brows; Thin high brows (`ff_brows_6`, FT) slot:brows; Brush brows (`ff_brows_7`, FT) slot:brows; Jug ears (`ff_ears_8`, FT) slot:ears; Uneven ears (`ff_ears_9`, FT) slot:ears; Gap teeth (`ff_teeth_10`, FT) slot:teeth; Buck teeth (`ff_teeth_11`, FT) slot:teeth; Pointy chin (`fn_pointychin`, NFT) slot:chin; Weak chin (`ff_chin_13`, FT) slot:chin; Big forehead (`ff_forehead_14`, FT) slot:forehead

### `facial_hair` (Facial hair, max 1)

Clean (`fh_none`, A); Stubble (`fh_stubble`, A); Full beard (`fh_beard`, A); Goatee (`fh_goatee`, A); Moustache (`fh_moustache`, A); Pencil (`fh_pencil`, A); Push-broom (`fh_pushbroom`, FTA); Braided (`fh_braid`, FTA)

### `distinctive` (Distinctive features, max 2)

Odd eyes (`df_hetero`, A); Face tattoo (`df_facetattoo`, A); Piercing (`df_septum`, A); Ear piercing (`df_ears`, A); Brow slits (`df_slits`, A); Bleached (`df_bleached`, A); No brows (`df_nobrows`, A); Gold grill (`df_grill`, A); Braces (`df_braces`, A); Brow scar (`df_scar`, A); Face gems (`df_gems`, A); Elf ears (`df_elf`, A); Big lashes (`df_lashes`, A); Nose tape (`df_bandage`, A)

### `accessory` (Accessories, max 3)

None (`acc_none`, A); Glasses (`acc_glasses`, A); Headphones (`acc_headphones`, A); Jewelry (`acc_jewelry`, A); Hat (`acc_hat`, A); Bag (`acc_bag`, A)

## 4. How the presets combine traits

- Style (`aesthetic`) distribution: Retro 14, Sporty 5, Streetstyle 5, Y2K 5, Goth 4, Theatre 3, Casual 2, Suits 1. Retro dominates; it is the 'odd but believable' default (flannel suits, cardigans, blazers, 70s and 80s costumes).
- Gender distribution: Male 24, Female 9, Trans man 3, Trans woman 2, Non-binary 1.
- Age distribution: Adult 20, Senior 12, Mature 6 (presets that list the key). The presets skew toward adult and senior; a young face needs an explicit age line in the brief.
- Build distribution: Slim 18, Athletic 7, Heavy 5, Ultra Muscular 4, Muscular 4, Curvy 1.
- Hair colour is mostly black or platinum; hair style is the main identity carrier in freak and total presets (bowl cut, lampshade bob, dome perm, volume waves, side tufts, horns, beehive, mullet).
- Every preset's brief states one SIGNATURE feature (the single loud thing the face or hair is built around) and the rest stays quiet. Typical signatures: a towering pompadour, a checkerboard-dyed flat-top, a mega jaw, a colossal handlebar moustache, a unibrow with ram-horn buns, a caveman brow ridge, a comically tiny head, a crescent-moon lacquered hairdo.
- Keys listed per preset: 5 keys: 1 presets, 6 keys: 1 presets, 8 keys: 1 presets, 13 keys: 1 presets, 14 keys: 1 presets, 17 keys: 2 presets, 18 keys: 32 presets. A few presets list only a handful of keys (the brief carries the rest), which is fine: the selection is a seed for the brief, not a full spec.

## 5. Reading the table for a new persona

1. Choose the tier by how stylized the persona should be. For a believable channel host or ad creator use `normal` and keep exaggeration low (one distinctive feature, ordinary head, neck and proportions). Use freak or total only for a deliberately odd, mascot-like character.
2. Pick the 8-10 keys that decide the silhouette and the face first: gender, age, build, height, ethnicity, skin tone, hair style, hair colour, eye shape and colour, facial hair. Then add AT MOST 1-2 distinctive features and one signature.
3. Respect maxima (`freak_face` 4, `accessory` 3, `proportions` 2, `distinctive` 2) and tier availability.
4. Translate the picks into the brief grammar in `casting-briefs.md` (Signature + Outfit + background clauses). Things not in the table (outfit, expression, lighting, background) are always written in the brief text.
5. Freeze the result as the persona bible (see `SKILL.md`, consistency procedure).

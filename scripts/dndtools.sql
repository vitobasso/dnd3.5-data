--class
select v.id, rulebook_id, page, 
c.name, hit_die, skill_points, starting_gold, 
advancement, class_features, 
prestige, required_bab, requirements, alignment
from dnd_characterclass c
left join dnd_characterclassvariant v on c.id=v.character_class_id
order by c.id, v.id

--class advancement (regex to clean tables)
^"? *\| *| *\| *"?$| *-- *(?=\|)|_\. *|(?<=\d)st (?=\|)|(?<=\d)nd (?=\|)|(?<=\d)rd (?=\|)|(?<=\d)th (?=\|)|(?<=\|) \+|(/\+\d*)+ *|(?<=\|) *| *(?=\|)|_\\.*$

--race
select r.id, rulebook_id, page, r.name, 
str, dex, con, int, wis, cha, 
si.name as size, speed, level_adjustment, natural_armor, t.name as type,
racial_hit_dice_count, hit_die_size, base_attack_type, base_fort_save_type, base_reflex_save_type, base_will_save_type,
racial_traits, combat
from dnd_race r
left join dnd_racetype t on r.race_type_id=t.id
left join dnd_racespeed s on s.race_id=r.id
left join dnd_racesize si on si.id=r.size_id
order by r.id, t.id


--books
select id, name, system, core from dnd_dndedition;

select id, dnd_edition_id, name, abbr, 
substr(ifnull(year,'') || ifnull(published,''),1,4) as year
from dnd_rulebook;


--feats
select id, rulebook_id, page, name
from dnd_feat;

select * from dnd_featcategory;

select * from dnd_feat_feat_categories;


--items
select i.id, rulebook_id, page,
i.name, s.name as slot, price_gp, weight
from dnd_item i
left join dnd_itemslot s on i.body_slot_id=s.id
where price_bonus is null and property_id is null or i.id=95;

select i.id, rulebook_id, page,
i.name, ifnull(s.name,'') || ifnull(p.name,'') as slot, 
price_gp, price_bonus
from dnd_item i
left join dnd_itemproperty p on i.property_id=p.id
left join dnd_itemslot s on i.body_slot_id=s.id
where (price_bonus is not null or property_id is not null) and i.id<>95;

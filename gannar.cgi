#!/usr/bin/env perl

#------ option start -------#

$cgi='gannar.cgi';
$adminpass='******';

@cname=('Gray','Red','Green','Blue','Yellow');
@lname=('灰','赤','緑','青','黄','砦','森','柵','河','山');
$width=30;# マップ横幅
$height=30;# マップ縦幅
$firstmove=10;# 初期移動力
$movemax=20;# 最大移動力
$firstwait=180;# 初期回復間隔
$waitmin=450;# 回復間隔最小
$waitadd=10;# 回復間隔加算
$waitmax=600;# 回復間隔最大
$pointmax=15;# 武勲最大
$cntrythre=3;# 最小領土
$ruinpoint=10;# 滅亡本人武勲
$ruinptpoint=3;# 滅亡味方武勲
$resetwait=43200;# 統一からリセットまで秒数
$beginwait=43200;# リセットから開始まで秒数

$logintime=600;# ログイン中とみなす秒数

$maxalllog=100;# 全体ログ
$maxcountrylog=500;# 国ログ
$maxactionlog=500;# 行動ログ
$maxhistorylog=999999;# 歴史ログ

@deletecount=([14,0],[7,20],[3,1]);

$title='ガンナー(コピー)';# タイトル
$bgcolor='#EEFFEE';# 背景色
$textcolor='black';# 文字色

$bbsurl='http://www7.atpages.jp/ssdi/gb/gb.cgi';
$chaturl='http://www7.atpages.jp/ssdi/chat/chat.cgi';

$playfile='player.txt';#players
$mapsfile='map.txt';#map
$mesafile='messeall.txt';#all message
$mescfile='messecountry.txt';#country message
$mesdfile='housin.txt';#housin message
$actsfile='actionlog.txt';#action
$histfile='history.txt';#history
$stockfile='stock.txt';#map stock for reset
$lock='lock.lok';#lock folder

#------ option end -------#

#---------------------------------------------------------------

@items=(
	{'name','強化槍','order',0,'gettype',0,'max',9,'val',1,'fid',1,'time',3600,'ename','攻撃力Up',},
	{'name','将軍旗','order',1,'gettype',0,'max',9,'val',0.3,'fid',2,'time',3600,'ename','影響力Up',},
	{'name','栄養剤','order',2,'gettype',0,'max',9,'val',10,'fid',3,'time',3600,'ename','栄養剤NG',},
	{'name','鋼鉄柵','order',4,'gettype',0,'max',9,'need',2,},
	{'name','掘削機','order',5,'gettype',0,'max',9,'need',4,},
	{'name','土砂袋','order',6,'gettype',0,'max',9,'need',7,},
	{'name','芭蕉扇','order',3,'gettype',0,'max',9,},
	{'name','双眼鏡','order',7,'gettype',0,'max',9,'val',1,},
);

#---------------------------------------------------------------

my($stdin,@flagitem,%form);
read(STDIN,$stdin,$ENV{'CONTENT_LENGTH'});%form=();
$stdin.="&".$ENV{'QUERY_STRING'};
foreach(split(/&/,$stdin)){
	my($key,$val)=split(/=/,$_);
	$val=~tr/+/ /;
	$val=~s/%([\dA-Fa-f][\dA-Fa-f])/chr(hex($1))/eg;
	$val=~s/&/&amp;/g;$val=~s/</&lt;/g;$val=~s/>/&gt;/g;$val=~s/\r\n|\r|\n/<br>/g;
	$form{$key}=$val;
}

for(my $i=0;$i<@items;$i++){
	$flagitem[$items[$i]{'fid'}]=$i if $items[$i]{'fid'};
}

&lock();

if($form{'mode'} eq 'admin'){
	&action_admin();
	&unlock();
	exit;
}

$ppls=&load_pls(undef,$form{'gnm'});
($pset,$pmap)=&load_map(undef,$$ppls{'pls'});
$plog=&load_log(undef);

if($form{'gnm'} ne ''){
	if($form{'mode'} eq 'new'){
		&action_new($ppls,$plog,$pset,$pmap);
	}
#	print &header();print &dump($p);exit;
	&action_main($ppls,$plog,$pset,$pmap);
}elsif($form{'mode'} eq 'playerlist'){
	print &action_playerlist($ppls,$plog,$pset,$pmap);
}else{
	print &action_top($ppls,$plog,$pset,$pmap);
}
&unlock();

exit;

#---------------------------------------------------------------

# TOP画面
sub action_top{
	my($pset,$pmap,$ppls,$plog);
	($ppls,$plog,$pset,$pmap)=@_;
	if((!-e $mapsfile || $$pset{'end'}) && $$pset{'resettime'}<time){
		&reset($ppls,$pmap,$plog,$pset);
		&save_pls(undef,$ppls);
		&save_map(undef,$pset,$pmap);
		&save_log(undef,$plog);
	}
	my $ret = "";
	$ret .= &header({'cid',2,'plnow',$$ppls{'now'},'pltotal',@{$$ppls{'pls'}}+0,});
	$ret .= &printfield($pset);
	$ret .= &printmap({'map',$pmap});
	$ret .= << "-HTML-";
<h2 class=oldmap><B>過去地形閲覧 等</B></h2>
<FORM ACTION='$cgi' method='POST' NAME='gannar'>
<SELECT NAME=val><OPTION VALUE=0>なし
</SELECT><INPUT TYPE=hidden NAME=mode VALUE='old'>
<INPUT TYPE='submit' VALUE='過去の地形確認'>
</FORM>
-HTML-
	$ret .= "<div class=firstlink>".&printlink()."</div>\n";
	$ret .= << "-HTML-";
<FORM ACTION='$cgi' method='POST' NAME='gannar' class=login>
<B>参加者名</B><INPUT TYPE='text' SIZE='18' NAME='gnm' VALUE='' MAXLENGTH='20'><BR>
<B>パスワード</B><INPUT TYPE='password' SIZE='10' NAME='gpw' MAXLENGTH='16'>
<input type=hidden name=mode value=login>
<INPUT TYPE='submit' VALUE='ログイン'></FORM>
-HTML-
	$ret .= << "-HTML-";
<FORM ACTION='$cgi' method='POST' NAME='gannar' class=login>
<B>参加者名</B><INPUT TYPE='text' SIZE='18' NAME='gnm' VALUE='' MAXLENGTH='20'><BR>
<B>パスワード</B><INPUT TYPE='password' SIZE='10' NAME='gpw' MAXLENGTH='16'>
<input type=hidden name=mode value=new>
<INPUT TYPE='submit' VALUE='新規登録'></FORM>
-HTML-
	$ret .= &printlog($plog,{'logcond',{'all',3,'country',10,'action',30,'history',3}});
	$ret .= &footer();

	return $ret;
}

# メイン画面
sub action_main{
	my($pset,$pmap,$ppls,$plog,$pl,$logcond,$message);
	($ppls,$plog,$pset,$pmap)=@_;
	$pl=$$ppls{'pls'}[$$ppls{'id'}];
	if($$pl{'name'} ne $form{'gnm'}){
		&error('ログイン時エラー：その名前は存在しません('.$form{'gnm'}.')');
	}elsif($$pl{'pass'} ne &pass($form{'gpw'})){
		&error('ログイン時エラー：パスワードが違います('.$form{'gpw'}.')');
	}

	if((!-e $mapsfile || $$pset{'end'}) && $$pset{'resettime'}<time){
		&reset($ppls,$pmap,$plog,$pset);
	}

	for($i=0;$i<@{$$ppls{'pls'}};$i++){
		next if $i==$$ppls{'id'};
		foreach(@deletecount){
			if($$ppls{'pls'}[$i]{'lastlogin'}+$$_[0]*86400<time && (!$$_[1] || $$ppls{'pls'}[$i]{'status'}[4]<$$_[1])){
				$txt=&printpl($$ppls{'pls'}[$i]).' [統一'.$$ppls{'pls'}[$i]{'status'}[0].'/褒賞'.$$ppls{'pls'}[$i]{'status'}[3].'/転生'.$$ppls{'pls'}[$i]{'status'}[4].'] は'.$$_[0].'日以上定期連絡が無いので除隊処分となりました';
				unshift(@{$$plog{'action'}},&printtime(time).' '.$txt.'<br>');
				splice(@{$$ppls{'pls'}},$i,1);
				$i--;
				last;
			}
		}
	}

	$$pl{'wait'}+=time-$$pl{'lastlogin'};
	if($$pl{'wait'}>=$$pl{'wamax'}){
		my $heal=int($$pl{'wait'}/$$pl{'wamax'});
		$heal=$$pl{'mvmax'}-$$pl{'move'} if $heal+$$pl{'move'}>$$pl{'mvmax'};
		$$pl{'move'}+=$heal if $heal>0;
		$message.='移動力が'.$heal.'回復しました。<br>' if $heal>0;
		$$pl{'wait'}=$$pl{'wait'}%$$pl{'wamax'};
	}
	if($$pl{'move'}>=$$pl{'mvmax'}){$$pl{'move'}=$$pl{'mvmax'};$$pl{'wait'}=0;}
	for(my $i=1;$i<@{$$pl{'itemflags'}};$i++){$$pl{'itemflags'}[$i]-=time-$$pl{'lastlogin'};$$pl{'itemflags'}[$i]=0 if $$pl{'itemflags'}[$i]<0;}
	$$pl{'lastlogin'}=time;
	$$pl{'actflag'}=1 if time>$$pset{'begintime'};

	print &header({'cid',$$pl{'belong'},'plnow',$$ppls{'now'},'pltotal',@{$$ppls{'pls'}}+0,});

	if($form{'mode'} eq 'passchg'){
		if(length($form{'newpass'})>3 && length($form{'newpass'})<11){
			$$pl{'pass'}=&pass($form{'newpass'});
			$form{'gpw'}=$form{'newpass'};
			$message.='パスワードを変更しました。<br>';
		}
	}elsif($form{'mode'} eq 'looking'){
		if($form{'val'}==1){$message.=&players($ppls,$pmap,$pl);}
		elsif($form{'val'}==2){$$pl{'logcond'}{'all'}=0;}
		elsif($form{'val'}==3){$$pl{'logcond'}{'country'}=0;}
		elsif($form{'val'}==4){$$pl{'logcond'}{'action'}=0;}
		elsif($form{'val'}==5){$$pl{'logcond'}{'history'}=0;}
		elsif($form{'val'}==6){$message.=&ranking($ppls,$pl);}
		elsif($form{'val'}==8){$message.="未実装です。";}
		elsif($form{'val'}==9){$message.=&config($pl);}
	}elsif($form{'mode'} eq 'shout'){
		$message.=&comment($pl,$plog,$form{'mes'},$form{'val'});
	}elsif($$pset{'begintime'}>time){
		$message.='まだ始まっていません。<br>開始までお待ちください。<br>';
	}elsif($form{'dir'}){
		if($$pl{'move'}>0){$message.=&move($form{'dir'},$$ppls{'pls'},$pl,$pmap,$plog,$pset);}
		else{$message.="移動力が足りません。<br>";}
	}elsif($form{'mode'} eq 'card'){
		$message.=&item($$ppls{'pls'},$pl,$pmap,$plog,$pset,$form{'val'});
	}

	while($$pl{'point'}>=$$pl{'ptmax'}){
		$$pl{'point'}-=$$pl{'ptmax'};
		$$pl{'status'}[3]++;
		$message.="武勲が$$pl{'ptmax'}を超えたため、各種褒賞を受け取ります。<br>\n";
		foreach(sort{$items[$a]{'order'}<=>$items[$b]{'order'}}(0..$#items)){
			if($items[$_]{'gettype'}==0 && $$pl{'item'}[$_]<$items[$_]{'max'}){
				$message.='<b>'.$items[$_]{'name'}.'</b>を入手しました。<br>';
				$$pl{'item'}[$_]++;
			}
		}
	}

	print "<h2><b>国の方針</b> $$plog{'housin'}[$$pl{'belong'}]</h2>" if $$plog{'housin'}[$$pl{'belong'}] ne '';
	print &printfield($pset);
	print "<table><tr><td valign=top>\n";
	print &printmap({'map',$pmap,'pl',$pl});
	print "</td><td valign=top>\n";
	print &status($pl,$$pmap[$$pl{'posi'}]{'land'});
	print &command($pl,$$pset{'begintime'});
	print "</td></tr></table>\n";
	print "<h2><B>個人ログ</B></h2>\n$message\n" if $message ne '';
	print &printlog($plog,$pl);
	print "<hr>\n<div class=footlink>".&printlink()."</div>\n";
	print &footer();
	&save_pls(undef,$ppls);
	&save_map(undef,$pset,$pmap);
	&save_log(undef,$plog);
}

sub action_playerlist{
	my($i,$ppls,$ret,@cntry,@cnm);
	$ppls=$_[0];
	$ret='';
	$ret.=&header({'cid',2,'plnow',$$ppls{'now'},'pltotal',@{$$ppls{'pls'}}+0,'css',<< "-CSS-"});
#list{border:1px solid #778077;border-collapse:collapse;}
#list td,#list th{border:1px solid #778077;padding:2px;}
.num{border-bottom:1px solid #778077;}
-CSS-
	foreach(@{$$ppls{'pls'}}){
		$cntry[$$_{'belong'}].=$$_{'name'}."<br>\n";
		$cnm[$$_{'belong'}]++;
	}
	$ret .= "<table id=list cellspacing=0><tr>";
	foreach($i=1;$i<@cname;$i++){
		$ret .= "<th class=B$i>$cname[$i]</th>" if $cntry[$i];
	}
	$ret .= "</tr><tr>\n";
	foreach($i=1;$i<@cname;$i++){
		$ret .= "<td valign=top><div class=num>$cnm[$i]人</div>\n$cntry[$i]\n</td>\n" if $cntry[$i];
	}
	$ret .= "</tr></table>\n";
	$ret .= &footer();
}

#---------------------------------------------------------------

# 移動
sub move{
	my($dir,$dirtxt,$pl,$pls,$map,$log,$posi,$return,$atkable,$txt,$enemy,$ruinflag);
	($dirtxt,$pls,$pl,$map,$log,$setting)=@_;
	$dir=$_[0] eq '北'?0:$_[0] eq '西'?1:$_[0] eq '東'?2:3;
	$posi=$$pl{'posi'};
	$$map[$$pl{'posi'}]{'arrow'}=('↑','←','→','↓')[$dir];
	while($posi==$$pl{'posi'} || !$$map[$posi]{'cost'}){
		$return.="$$map[$posi]{'name'}地形のため、さらに前進しました。<br>" if $posi!=$$pl{'posi'};
		$tposi=&movept($dir,$posi);
		if($tposi==$posi){return "$return移動しようとしましたが、移動先が端っこのため失敗しました。<br>";}
		if(!$$map[$tposi]{'movable'}){return $return.'移動しようとしましたが、移動先'.&printpt('',$tposi).'が'.&printmp($$map[$tposi]{'land'},$$map[$tposi]{'name'}).'のため失敗しました。<br>';}
		if($$map[$tposi]{'cost'}>$$pl{'move'}){return $return.'移動しようとしましたが、移動先'.&printpt('',$posi).'が'.&printmp($$map[$tposi]{'land'},$$map[$tposi]{'name'}).'のため移動力が足りません。<br>';}
		$posi=$tposi;
	}
	$return.=&printpt($$map[$$pl{'posi'}]{'land'},$$pl{'posi'}).'から'.&printpt($$map[$posi]{'land'},$posi).'へ移動しました。<br>';
	if($$map[$posi]{'cost'}>1){$return.=$$map[$posi]{'name'}.'地形のため、移動力を'.$$map[$posi]{'cost'}.'消費します。<br>';}
	$$pl{'move'}-=$$map[$posi]{'cost'};
	$$map[$posi]{'member'}[$$pl{'belong'}]++;
	$$map[$$pl{'posi'}]{'member'}[$$pl{'belong'}]--;
	$enemy=$$map[$posi]{'belong'};
	if($$map[$posi]{'ownable'} && $enemy!=$$pl{'belong'}){
		$return.=&battle($dirtxt,$pls,$pl,$map,$log,$setting,$posi);
	}elsif($$map[$posi]{'hp'}){
		$return.=&fence($dirtxt,$pls,$pl,$map,$log,$setting,$posi);
	}
	$$pl{'posi'}=$posi;
	return $return."\n";
}

sub fence{
	my($dir,$dirtxt,$pl,$pls,$map,$log,$posi,$return,$atkable,$txt,$enemy,$mynm,$mytxt);
	($dirtxt,$pls,$pl,$map,$log,$setting,$posi)=@_;
	($atkable,$mynm,$mytxt)=&calcbattle(1,$posi,$pl,$map,$pls);
	return if !$atkable;
	$txt=&printpl($pl).'が'.&printpt($$map[$posi]{'land'},$posi).'にて'.&printcn($$pl{'belong'},"$mytxt").'で'.&printmp($$map[$posi]{'land'},$$map[$posi]{'name'});
	if($$map[$posi]{'hp'}>$mynm){
		$txt.='を壊そうとしましたが失敗しました。<br>';
	}else{
		$txt.='を破壊しました。<br>';
		$$map[$posi]{'land'}=$$pl{'belong'};
		$$map[$posi]{'belong'}=$$pl{'belong'};
	}
	$return.=$txt;
	unshift(@{$$log{'action'}},&printtime(time).' '.$txt);
	return $return;
}

# 占領
sub battle{
	my($dir,$dirtxt,$pl,$pls,$map,$log,$posi,$return,$atkable,$txt,$enemy,$ruinflag,$mynm,$mytxt,$vsnm,$vstxt);
	($dirtxt,$pls,$pl,$map,$log,$setting,$posi)=@_;
	($atkable,$mynm,$mytxt,$vsnm,$vstxt)=&calcbattle(3,$posi,$pl,$map,$pls);
	return if !$atkable;
	$return.=&printpt($$map[$posi]{'land'},$posi).'に占領行為を実施します。<br>';
	$enemy=$$map[$posi]{'belong'};
	$txt=&printpl($pl).' が '.&printpt($$map[$posi]{'land'},$posi);
	if($vsnm){
		$txt.=sprintf('にて<span class=B%s>%s</span>VS<span class=B%s>%s</span>の争いで',$$pl{'belong'},$mytxt,$enemy,$vstxt);
	}else{
		$txt.='を';
	}
	if($mynm>$vsnm){
		$txt.='勝利して' if $vsnm;
		$txt.='占領しました。<br>';
		$return.=$txt;
		if($$pl{'wamax'}>$waitmin){
			$$pl{'wamax'}--;
			$return.='回復間隔が1減少しました。<br>';
		}
		if($vsnm>0){
			$$pl{'point'}++;
			$return.='武勲が1上昇しました。<br>';
		}
		$$setting{'country'}[$$pl{'belong'}]++;
		$$setting{'country'}[$enemy]--;
		if($$setting{'country'}[$enemy]<$cntrythre){$ruinflag=1;}
		elsif($enemy && $posi==&defaultpt($enemy)){$ruinflag=2;}
		$$map[$posi]{'land'}=$$pl{'belong'};
		$$map[$posi]{'belong'}=$$pl{'belong'};
	}else{
		$txt.='敗北しました。<br>';
		$return.=$txt;
	}
	unshift(@{$$log{'action'}},&printtime(time).' '.$txt);
	if($ruinflag){
		$return.=&ruin($dirtxt,$pls,$pl,$map,$log,$setting,$enemy,$ruinflag);
	}
	return $return;
}

# 滅亡
sub ruin{
	my($dir,$dirtxt,$pl,$pls,$map,$log,$posi,$return,$atkable,$txt,$enemy,$ruinflag,$i);
	($dirtxt,$pls,$pl,$map,$log,$setting,$enemy,$ruinflag)=@_;
	unshift(@{$$log{'history'}},$$log{'action'}[0]);
	unshift(@{$$log{'action'}},&printtime(time).' '.sprintf('<span class=B%s>%s</span>が%s、<span class=B%s><b>%s</b>(領土%d)</span>が<span class=B%s><b>%s</b>(領土%d)</span>を滅亡させました。<br>',$$pl{'belong'},$$pl{'name'},("領地$cntrythre未満宣言を行い","本拠地を陥落させ")[$ruinflag-1],$$pl{'belong'},$cname[$$pl{'belong'}],$$setting{'country'}[$$pl{'belong'}],$enemy,$cname[$enemy],$$setting{'country'}[$enemy]));
	unshift(@{$$log{'history'}},$$log{'action'}[0]);
	unshift(@{$$log{'action'}},&printtime(time).' '.sprintf('<span class=B%s>%s</span>は<b class=B%s>%s</b>の領土%dを全て奪い取りました。<br>',$$pl{'belong'},$cname[$$pl{'belong'}],$enemy,$cname[$enemy],$$setting{'country'}[$enemy])) if $$setting{'country'}[$enemy];
	$return.="<span class=B$enemy>$cname[$enemy]</span>を滅亡させました。<br>";
	$$pl{'point'}+=$ruinpoint;
	$$pl{'mvmax'}++ if $$pl{'mvmax'}<$movemax;
	$$setting{'country'}[$enemy]=0;
	for($i=0;$i<$width*$height;$i++){
		if($$map[$i]{'belong'}==$enemy && $$map[$i]{'ownable'}){
			$$setting{'country'}[$$pl{'belong'}]++;
			$$map[$i]{'land'}=$$pl{'belong'};
			$$map[$i]{'belong'}=$$pl{'belong'};
		}
	}
	$i=0;foreach(@{$$setting{'country'}}){$i++ if $_;}$i-- if $$setting{'country'}[0];
		my(@tmp,@cnt,@exl);
		foreach(@{$pls}){
			$cnt[$$_{'belong'}]++;
			if($$_{'belong'}==$enemy){
				push(@tmp,$_);
				$$_{'status'}[2]++;
				$$_{'mvmax'}=$movemax if $$_{'mvmax'}>$movemax;
				$$_{'wamax'}+=$waitadd if $$_{'status'}[4]>=$waitthre;
				$$_{'wamax'}=$waitmax if $$_{'wamax'}>$waitmax;
				$$_{'move'}=$$_{'mvmax'};
			}elsif($$_{'belong'}==$$pl{'belong'}){
				$$_{'status'}[1]++;
				$$_{'point'}+=$ruinptpoint;
			}
		}
	if($i>1){
		unshift(@{$$log{'action'}},&printtime(time).' '.sprintf('<span class=B%s>%s</span>から多数の人材が亡命していきました。<br>',$enemy,$cname[$enemy])) if $enemy;
		for($i=0;$i<@tmp;$i++){$j=int rand(@tmp-$i)+$i;@tmp[$i,$j]=@tmp[$j,$i] if $i!=$j;}
		foreach(@tmp){
			foreach($i=0,$j=1;$j<@cname;$j++){$i=$j if $cnt[$j] && $j!=$enemy && (!$i || $cnt[$i]>$cnt[$j]);}
			$$_{'belong'}=$i;
			$$_{'posi'}=&defaultpt($i);
			$cnt[$i]++;
			$exl[$i].='、' if $exl[$i];$exl[$i].=sprintf('<span class=B%s>%s</span>',$enemy,$$_{'name'});
		}
		for($i=1;$i<@exl;$i++){if($exl[$i]){
			unshift(@{$$log{'action'}},&printtime(time).' '.sprintf('<span class=B%s>%s</span>への亡命者：%s<br>',$i,$cname[$i],$exl[$i]));
		}}
	}else{
		$return.=&reign($dirtxt,$pls,$pl,$map,$log,$setting,$enemy,$ruinflag);
	}
	return $return;
}

# 統一
sub reign{
	my($dir,$dirtxt,$pl,$pls,$map,$log,$posi,$return,$atkable,$txt,$enemy,$ruinflag,$i,$time,@tmp,@cnt);
	($dirtxt,$pls,$pl,$map,$log,$setting,$enemy,$ruinflag)=@_;
	$txt=sprintf('<span class=B%s>',$$pl{'belong'});
	$time=time-$$setting{'begintime'};
	if($time>3600){$txt.=sprintf('%d時間%02d分',int($time/3600),int(($time%3600)/60+0.5));}
	else{$txt.=sprintf('%d分%02d秒間',int($time/60),$time%60);}
	$txt.='の戦乱の末、<b>'.$$pl{'name'}.'</b>が終戦宣言を行い<b>'.$cname[$$pl{'belong'}].'</b>による第'.$$setting{'period'}.'期全土統一が成し遂げられました</span><br>';
	$return.='統一しました。<br>';
	foreach(@{$pls}){
		if($$_{'origin'}==$$pl{'belong'}){
			$$_{'status'}[0]++;
			$$_{'mvmax'}++;
		}
		$$_{'move'}=$$_{'mvmax'};
	}
	unshift(@{$$log{'history'}},&printtime(time).' '.$txt);
	unshift(@{$$log{'action'}},$$log{'history'}[0]);
	$$setting{'resettime'}=time+$resetwait;
	$$setting{'begintime'}=time+$resetwait+$beginwait;
	$$setting{'end'}=1;
	return $return;
}

# アイテム
sub item{
	my($dir,$dirtxt,$pl,$pls,$map,$log,$posi,$return,$atkable,$txt,$enemy,$ruinflag,$i,$time,@tmp,@cnt);
	($pls,$pl,$map,$log,$setting,$item)=@_;
	if($$pl{'item'}[$item]<=0){
		return $items[$item]{'name'}.'を使用しようとしましたが、個数が足りないため失敗しました。<br>';
	}
	$txt='<b>'.$items[$item]{'name'}.'</b>を使用しました。';
	unshift(@{$$log{'action'}},&printtime(time).' '.&printpl($pl).'が'.&printpt($$map[$$pl{'posi'}]{'land'},$$pl{'posi'}).'にて'.$txt);
	$return.=$txt.'<br>';
	$$pl{'item'}[$item]--;
	if($item==0){
		$return.='攻撃力を'.$items[$item]{'time'}.'秒の間増加させます。<br>';
		$$pl{'itemflags'}[$items[$item]{'fid'}]+=$items[$item]{'time'};
	}elsif($item==1){
		$return.='影響力を'.$items[$item]{'time'}.'秒の間増加させます。<br>';
		$$pl{'itemflags'}[$items[$item]{'fid'}]+=$items[$item]{'time'};
	}elsif($item==2){
		if($$pl{'itemflags'}[$items[$item]{'fid'}]>0){
			$$pl{'item'}[$item]++;
			shift(@{$$plog{'action'}});
			return 'このアイテムの使用は禁止されています。アイテム使用はキャンセルされました。<br>';
		}else{
			$$pl{'move'}+=$items[$item]{'val'};
			$$pl{'itemflags'}[3]=$items[$item]{'time'};
			$return.='移動力を'.$items[$item]{'val'}.'回復しました。<br>';
		}
	}elsif($item==3 || $item==4){
		if($$map[$$pl{'posi'}]{'belong'}!=$$pl{'belong'}){
			$txt='現在地が自陣でないため失敗しました。';
		}elsif($$pl{'posi'}==&defaultpt($$pl{'belong'})){
			$txt='本拠地のため失敗しました。';
		}else{
			$txt=$$map[$$pl{'posi'}]{'member'}[$$pl{'belong'}].'人で';
			if($$map[$$pl{'posi'}]{'member'}[$$pl{'belong'}]<$items[$item]{'need'}){
				$txt.='作成しようとしましたが、人数が足りなかったため失敗しました。';
			}else{
				$$map[$$pl{'posi'}]{'land'}=$item==3?7:8;
				$$map[$$pl{'posi'}]{'belong'}=0;
				$txt.=&printmp($$map[$$pl{'posi'}]{'land'},$lname[$$map[$$pl{'posi'}]{'land'}]).'を作成しました。';
			}
		}
		$$log{'action'}[0].=$txt;
		$return.=$txt.'<br>';
	}elsif($item==5){
		if($$map[$$pl{'posi'}]{'land'}!=8){
			$txt='現在地が'.&printmp(8,$lname[8]).'ではないため失敗しました。';
		}else{
			$txt=$$map[$$pl{'posi'}]{'member'}[$$pl{'belong'}].'人で';
			if($$map[$$pl{'posi'}]{'member'}[$$pl{'belong'}]<$items[$item]{'need'}){
				$txt.='埋め立てを実行しましたが、人数が足りなかったため失敗しました。';
			}else{
				$txt.=&printmp($$map[$$pl{'posi'}]{'land'},$$map[$$pl{'posi'}]{'name'}).'の埋め立てに成功しました。';
				$$map[$$pl{'posi'}]=&getmap($$pl{'belong'},'',$$map[$$pl{'posi'}]{'member'});
			}
		}
		$$log{'action'}[0].=$txt;
		$return.=$txt.'<br>';
	}elsif($item==6){
		for($i=0;$i<$width*$height;$i++){push(@tmp,$i) if $$map[$i]{'belong'}!=$$pl{'belong'} && $$map[$i]{'movable'} && $$map[$i]{'cost'};}
		$$map[$$pl{'posi'}]{'member'}[$$pl{'belong'}]--;
		$$pl{'posi'}=$tmp[rand(@tmp)];
		$$map[$$pl{'posi'}]{'member'}[$$pl{'belong'}]++;
		$txt=&printpt($$map[$$pl{'posi'}]{'land'},$$pl{'posi'}).'へとランダムワープしました。';
		$$log{'action'}[0].=$txt;
		$return.=$txt.'<br>';
	}elsif($item==7){
		$return.='周辺の敵の人数と罠を確認します。<br>';
		for($i=0-$items[7]{'val'};$i<=$items[7]{'val'};$i++){
			next if $i*$width+$$pl{'posi'}<0 || $i*$width+$$pl{'posi'}>$height*$width;
			for($j=0-$items[7]{'val'};$j<=$items[7]{'val'};$j++){
				my($posi,$k,$txt);
				next if $$pl{'posi'}%$width+$j<0 || $$pl{'posi'}%$width+$j>$width;
				my $posi=$$pl{'posi'}+$i*$width+$j;
				my $k=0;
				foreach(@{$$map[$posi]{'member'}}){
					if($k!=$$pl{'belong'} && $_){
						$txt.=&printcn($k,$_.'人');
						$$map[$posi]{'text'}.=&printcn($k,'<b style="color:red">'.$_.'</b>');
					}
					$k++;
				}
				$return.=&printpt($$map[$posi]{'belong'},$posi).$txt.'、' if $txt;
			}
		}
		$return.='<br>';
	}
	$$log{'action'}[0].='<br>';
	return $return;
}

# 発言/伝言
sub comment{
	my($pl,$text,$type,$typetxt,$return);
	$pl=$_[0];$log=$_[1];$txt=$_[2];$type=$_[3];
	return if $type!=2 && $txt eq '';
	return if $type==0;
	if($type==2){
		$$pl{'board'}=$txt;
		$return.=$txt eq ''?'伝言を消去するように':"「$txt」<br>と";
		$return.="本拠地へと伝えた。<br>";
	}elsif($type==3){
		$return.="「$txt」<br>と全体に向かって叫んだ。<br>";
		unshift(@{$$log{'all'}},&printtime(time)." <span class=B$$pl{'belong'}>$$pl{'name'}</span>:".$txt."<br>");
	}elsif($type==1){
		$return.="国の方針を「$txt」に変更した。";
		$$log{'housin'}[$$pl{'belong'}]=&printtime(time)." <span class=B$$pl{'belong'}>$$pl{'name'}</span>：".$txt;
	}elsif($type==$$pl{'belong'}+10){
		$type-=10;
		$return.="「$txt」<br>と国内用無線機に囁いた。<br>";
		unshift(@{$$log{'country'}},&printtime(time)." <span class=B$$pl{'belong'}>$$pl{'name'}</span>：".$txt."<br>&$type&$type&");
	}elsif($type<@cname+10){
		$type-=10;
		$return.="「$txt」<br>と$cname[$type]国に伝えた。<br>";
		unshift(@{$$log{'country'}},&printtime(time)." ".&printpl($pl)."→<span class=B$type>$cname[$type]</span>：".$txt."<br>&$$pl{'belong'}&$type&");
	}
	return $return;
}

#---------------------------------------------------------------

# タイトル下情報
sub printfield{
	my($i,$return,%param);
	%param=%{$_[0]};
	$return.="<h2 class=world><B>第$param{'period'}期大陸状況　</B>";
	$return.="<span class=B4>".&printtime($param{'resettime'})."</span>にMAP初期化。" if $param{'resettime'}>time;
	$return.="<span class=B4>".&printtime($param{'begintime'})."</span>に開始します。" if $param{'begintime'}>time;
	for($i=0;$i<@cname;$i++){
		$return.=" $cname[$i]：$param{'country'}[$i]" if $param{'country'}[$i];
	}
	$return.="</h2>\n";
	return $return;
}

# マップ出力
sub printmap{
	my($i,$return,%param);
	%param=%{$_[0]};
	@map=@{$param{'map'}};
	$return.="<table id=map>\n<tr class=outer><td>-</td>";
	foreach($i=0;$i<$width;$i++){$return.="<td>$i</td>";}
	$return.="<td>-</td></tr>\n";
	$posi=0;
	foreach($i=0;$i<$width*$height;$i++){
		$return.=sprintf("<tr><td class=outer>%d</td>",int($i/$width)) if $i%$width==0;
		$return.="<td class=B$map[$i]{'land'}";
		$return.=">$map[$i]{'arrow'}";
		$return.=$i==$param{'pl'}{'posi'}?"<b>[$map[$i]{'member'}[$param{'pl'}{'belong'}]]</b>":$map[$i]{'member'}[$param{'pl'}{'belong'}] if $map[$i]{'member'}[$param{'pl'}{'belong'}];
		$return.=$map[$i]{'text'}."</td>";
		$return.=sprintf("<td class=outer>%d</td></tr>\n",int($i/$width)) if $i%$width+1==$width;
	}
	$return.="<tr class=outer><td>-</td>";
	foreach($i=0;$i<$width;$i++){$return.="<td>$i</td>";}
	$return.="<td>-</td></tr>\n</table>";
	return $return;
}

# 伝言表示
sub players{
	my($ppls,$map,$pl,$return);
	$ppls=$_[0];$map=$_[1];$pl=$_[2];
	$return=<< '-HTML-';
国内用無線機にて全員の所在地と伝言を確認した。<BR>
【参加者名[移動力]「伝言内容」】<BR>
※最終ログイン時間順に表示されています<BR>
※<B><U>10分以内のログイン者は太字＋下線</U></B>、<span class=B0>未行動者は灰色</span>で表示しています<BR>
※<U>場所が下線</U>…自分と同じ位置　移動力…最終ログイン時の値　[携帯]…携帯ログイン者　[初]…転生数ゼロ
<HR>
-HTML-
	foreach(sort{$$b{'lastlogin'}<=>$$a{'lastlogin'}}@{$$ppls{'pls'}}){
		my($name,$posi);
		next if $$pl{'belong'}!=$$_{'belong'};
		$name=&printpl($_);
		$name="<u>$name</u>" if $$_{'lastlogin'}+600>time;
		$name="<b>$name</b>" if $$_{'lastlogin'}+3600>time;
		$posi=&printpt($$map[$$_{'posi'}]{'land'},$$_{'posi'});
		$posi="<u>$posi</u>" if $$pl{'posi'}==$$_{'posi'};
		$return.='<span class=notmove>' if !$$pl{'actflag'};
		$return.="$name$posi\[$$_{'move'}]";
		$return.="「$$_{'board'}」" if $$_{'board'} ne '';
		$return.='</span>' if !$$pl{'actflag'};
		$return.="<br>";
	}
	return $return;
}

# 戦歴
sub ranking{
	my($ppls,$point,$ranktxt,$c,$i);
	$ppls=$_[0];$pl=$_[1];$c=1;$i=0;
	foreach(@{$$ppls{'pls'}}){$c++ if $$pl{'score'}<$$_{'score'};$i++ if $$pl{'score'}==$$_{'score'};}
	$ranktxt=$c.'位';
	$ranktxt.='タイ(同順位'.$i.'人)' if $i>1;
	return '<span style="color:red">戦歴の公式：　(統一×１００＋破壊×１０－滅亡×５＋褒賞) ÷ (４＋転生÷２)　※切り捨て</span><BR>無線機からの情報で自分自身の戦歴を確認した。<BR><BR>現在の戦歴は <B>'.$$pl{'score'}.'</B> です。全参加者'.@{$$ppls{'pls'}}.'人中 <B class=B4>'.$ranktxt.'</B>となっています。<br>'."\n";
}

# 設定
sub config{
	my($pl);
	return << "-HTML-";
<form action='$cgi' method=POST>
<input type=hidden name=mode value=passchg>
<input type=hidden name=gnm value="$form{'gnm'}">
<input type=hidden name=gpw value="$form{'gpw'}">
<h3>【パスワードを変更する】</h3>
新パスワード(4～10桁)：<input type=password name=newpass>
<input type=submit value="変更">
</form>
-HTML-
}

# ステータス
sub status{
	my($pl,$posicn,$posi,$return);
	$pl=$_[0];
	$pointmax=15;
	$posi=&printpt($_[1],$$pl{'posi'});
	$return.=<< "-HTML-";
<h2><B>ステータス</B></h2>
<table>
<TR><TD VALIGN='top'><TABLE><TR><TH>参加者名</TH><TD COLSPAN=3>$$pl{'name'}</TD></TR>
<TR><TH>所属国</TH><TD><span class=B$$pl{'belong'}>$cname[$$pl{'belong'}]</span></TD><TH>統一数</TH><TD>$$pl{'status'}[0]</TD></TR>
<TR><TH>出身国</TH><TD><span class=B$$pl{'origin'}>$cname[$$pl{'origin'}]</span></TD><TH>破壊数</TH><TD>$$pl{'status'}[1]</TD></TR>
<TR><TH>現在地</TH><TD>$posi</TD><TH>滅亡数</TH><TD>$$pl{'status'}[2]</TD></TR>
<TR><TH>武勲</TH><TD>$$pl{'point'}/$$pl{'ptmax'}</TD><TH>褒賞数</TH><TD>$$pl{'status'}[3]</TD></TR>
<TR><TH>移動力</TH><TD>$$pl{'move'}/$$pl{'mvmax'}</TD><TH>転生数</TH><TD>$$pl{'status'}[4]</TD></TR>
<TR><TH>回復間隔</TH><TD COLSPAN=3>$$pl{'wait'}/$$pl{'wamax'}</TD></TR>
<TR><TH>名声値</TH><TD COLSPAN=3>$$pl{'honor'}</TD></TR>
-HTML-
	for($i=1;$i<@{$$pl{'itemflags'}};$i++){
		$return.="<tr><th>$items[$flagitem[$i]]{'ename'}</th><td colspan=3>残り$$pl{'itemflags'}[$i]秒</td></tr>\n" if $$pl{'itemflags'}[$i];
	}
	$return.='<TR class=B0><TH>[未行動]</TH><TD COLSPAN=3>各種恩恵受取対象外</TD></TR>'."\n" if !$$pl{'actflag'};
	$return.="</table>\n</td></tr></table>\n";
	return $return;
}

# コマンド表示
sub command{
	my($i,$pl,$begintime,$return,@tmp);
	$pl=$_[0];$begintime=$_[1];
	$pointmax=15;
	$return.=<< "-HTML-";
<h2><B>コマンド</B></h2>
<table><tr><td>
<BR>-移動-<BR>
-HTML-
	$return.=<< "-HTML-" if time>$begintime;
<form ACTION="$cgi" method=POST>
<INPUT TYPE=hidden NAME=gnm VALUE='$form{'gnm'}'>
<INPUT TYPE=hidden NAME=gpw VALUE='$form{'gpw'}'>
<INPUT TYPE=hidden NAME=mode VALUE='move'>
<table class=direct><tr><td><td><input type=submit name='dir' value='北'><td></tr>
<tr><td><input type=submit name='dir' value='西'><td><td><input type=submit name='dir' value='東'></tr>
<tr><td><td><input type=submit name='dir' value='南'><td></tr></table>
</form>
-HTML-
	$return.='待ち時間のため移動出来ません。<BR>開始時間までお待ちください。<BR><BR>'."\n" if $begintime>time;
	$return.=<< "-HTML-";
</TD><TD ROWSPAN=2 VALIGN=top>
<FORM ACTION="$cgi" method=POST NAME=itemBox onSubmit='return funcSubmit()'><INPUT TYPE=hidden NAME=gnm VALUE='$form{'gnm'}'><INPUT TYPE=hidden NAME=gpw VALUE='$form{'gpw'}'><INPUT TYPE=hidden NAME=mode VALUE='card'>
-アイテム-<BR>
<SELECT NAME='val'><OPTION VALUE='777'>--
-HTML-
	foreach(sort{$items[$a]{'order'}<=>$items[$b]{'order'}}(0..$#items)){
		$return.="<option value=$_>$items[$_]{'name'} $$pl{'item'}[$_]個\n" if $$pl{'item'}[$_];
	}
	$return.='</SELECT><BR>';
	$return.=$begintime>time?'使用不可':"<INPUT TYPE=submit VALUE='使用'>\n";
	$return.=<< "-HTML-";
</FORM>
</TD></TR><TR><TD>
<FORM ACTION="$cgi" method=POST NAME=gannar><INPUT TYPE=hidden NAME=gnm VALUE='$form{'gnm'}'><INPUT TYPE=hidden NAME=gpw VALUE='$form{'gpw'}'><INPUT TYPE=hidden NAME=mode VALUE='looking'>
-確認-<BR><SELECT NAME=val><OPTION VALUE=1>味方の場所と伝言
<OPTION VALUE=8>国内の情報ログ
<OPTION VALUE=2>全ての全体発言
<OPTION VALUE=3>全ての国内発言
<OPTION VALUE=4>全ての行動ログ
<OPTION VALUE=5>全ての歴史ログ
<OPTION VALUE=6>自分の戦歴
<OPTION VALUE=9>設定画面
</SELECT><BR><INPUT TYPE=submit VALUE='確認'></FORM>
</TD></TR><TR><TD COLSPAN=2>
<FORM ACTION="$cgi" method=POST NAME=gannar><INPUT TYPE=hidden NAME=gnm VALUE='$form{'gnm'}'><INPUT TYPE=hidden NAME=gpw VALUE='$form{'gpw'}'><INPUT TYPE=hidden NAME=mode VALUE='shout'>
-発言/伝言-<BR><INPUT TYPE=text NAME=mes SIZE=44 MAXLENGTH=300 VALUE=''><BR><SELECT NAME=val><OPTION VALUE=''>-----
-HTML-
	$return.=sprintf("<OPTION VALUE=%d>国内へ\n",$$pl{'belong'}+10);
	$return.="<OPTION VALUE=3>全体へ\n";
	for($i=0;$i<@cname;$i++){
		$return.=sprintf("<OPTION VALUE=%d>%sへ\n",$i+10,$cname[$i]) if $i!=$$pl{'belong'};
	}
	$return.=<< "-HTML-";
<OPTION VALUE=1>国の方針
<OPTION VALUE=2>伝言
</SELECT><INPUT TYPE=submit VALUE='叫ぶ/更新'></FORM></TD></TR>
</TABLE>
-HTML-
	return $return;
}

# ログ表示
sub printlog{
	my($pl,$return,%param);
	$pl=$_[1];
	%param=%{$_[0]};
	for $key('all','country','action','history'){
		$c=1;foreach(@{$param{$key}}){
			if($$pl{'logcond'}{$key} && $c>$$pl{'logcond'}{$key}){last;}
			$txt=$_;
			if(/&$/){if($pl && /&$$pl{'belong'}&/o){$txt=~s/&\d+&\d+&//;}else{next;}}
			if($c==1){
				$return.='<h2 class=mes><B>';
				$return.=$key eq 'all'?'全体発言':$key eq 'country'?'国別発言':$key eq 'action'?'行動ログ':$key eq 'history'?'歴史ログ':'全体';
				$return.='</B>(';
				$return.=$$pl{'logcond'}{$key}?$$pl{'logcond'}{$key}:'全';
				$return.='件表示)</h2>'."\n";
			}
			$return.=$txt."\n";
			$c++;
		}
	}
	return $return;
}

# リンク表示
sub printlink{
	return << "-HTML-";
<s HREF='./regist.html'>新規登録</s> , <s HREF='./manual.html'>説明書</s> , <s HREF='./question.html'>Q&A</s> , <A HREF='$cgi?mode=playerlist'>名簿</A> , <s HREF='./version.html'>仕様変更履歴(616期)</s> , <s HREF='./link.html'>Link</s> , <A HREF='$bbsurl'>掲示板</A> , <A HREF='$chaturl'>チャット</A>
-HTML-
}

#---------------------------------------------------------------

# 各種読み込み
sub load_pls{
	my($i,$plid,$now,$name,@pls,@dat);
	open(my $f,$playfile);
	$i=0;$plid=0;$now=0;
	$name=$_[1];
	while(<$f>){
		chomp;
		@dat=split(/<>/);
		my %dt=();
		$dt{'name'}=$dat[0];
		$dt{'pass'}=$dat[1];
		$dt{'belong'}=$dat[2];
		$dt{'origin'}=$dat[3];
		$dt{'item'}=[split(//,$dat[4])];
		$dt{'posi'}=$dat[5];
		$dt{'wait'}=$dat[6];
		$dt{'wamax'}=$dat[7];
		$dt{'move'}=$dat[8];
		$dt{'mvmax'}=$dat[9];
		$dt{'point'}=$dat[10];
		$dt{'lastlogin'}=$dat[11];
		$dt{'honor'}=$dat[12];
		$dt{'status'}=[split(/!/,$dat[13])];
		$dt{'itemflags'}=[split(/!/,$dat[14])];
		$dt{'actflag'}=$dat[15];
		$dt{'config'}=$dat[16];
		$dt{'board'}=$dat[17];
		push(@pls,&transpl(\%dt));
		if($name ne '' && $name eq $dt{'name'}){$plid=$i;}
		$now++ if $dt{'lastlogin'}+$logintime>time;
		$i++;
	}
	close($f);
	return {'id',$plid,'now',$now,'pls',\@pls,};
}
sub load_map{
	my($p,$ppl,$map,$trap,$i,$j,$pmap,@set,@balance);
	$ppl=$_[1];
	open(my $f,$mapsfile);
	@set=split(/!/,<$f>);pop(@set);
	$map=<$f>;
	$trap=<$f>;
	close($f);
	for($i=0;$i<$height;$i++){
		for($j=0;$j<$width;$j++){
			$land=substr($map,$i*$width+$j,1);
			$p=&getmap($land,length($trap)>$i*$width+$j?substr($trap,$i*$width+$j,1):'');
			$$pmap[$i*$width+$j]=$p;
			$balance[$$p{'belong'}]++ if $$p{'ownable'};
		}
	}
	for($i=0;$i<@$ppl;$i++){
		$$pmap[$$ppl[$i]{'posi'}]{'member'}[$$ppl[$i]{'belong'}]++;
	}
	return {'period',$set[0],'resettime',$set[1],'begintime',$set[2],'end',$set[3],'country',\@balance},$pmap;
}
sub load_log {
	my($txt);
	$$txt{'all'}=[];
	open(my $f,$mesafile);while(<$f>){chomp;push(@{$$txt{'all'}},$_);}close($f);
	open(my $f,$mescfile);
	for(my $i=0;$i<@cname;$i++){
		$_=<$f>;chomp;
		$$txt{'housin'}[$i]=$_;
	}
	$$txt{'country'}=[];
	while(<$f>){chomp;push(@{$$txt{'country'}},$_);}
	close($f);
	$$txt{'action'}=[];
	open(my $f,$actsfile);while(<$f>){chomp;push(@{$$txt{'action'}},$_);}close($f);
	open(my $f,$histfile);while(<$f>){chomp;push(@{$$txt{'history'}},$_);}close($f);
	return $txt;
}

# 各種保存
sub save_pls {
	my($i,$plid,$now,@pls);
	open(my $f,">$playfile");
	foreach $dt(@{$_[1]{'pls'}}){
		print $f join('<>',
			$$dt{'name'},
			$$dt{'pass'},
			$$dt{'belong'},
			$$dt{'origin'},
			join("",@{$$dt{'item'}}),
			$$dt{'posi'},
			$$dt{'wait'},
			$$dt{'wamax'},
			$$dt{'move'},
			$$dt{'mvmax'},
			$$dt{'point'},
			$$dt{'lastlogin'},
			$$dt{'honor'},
			join('!',@{$$dt{'status'}}),
			join('!',@{$$dt{'itemflags'}}),
			$$dt{'actflag'},
			$$dt{'config'},
			$$dt{'board'},
			"\n");
	}
	close($f);
}

sub save_map {
	my($map,$trap,$i,$j,$pmap,@set,@balance);
	for($i=0;$i<@{$_[2]};$i++){
		$map.=$_[2][$i]{'land'};
		$trap.=$_[2][$i]{'trap'};
	}
	open(my $f,">$mapsfile");
	print $f join('!',$_[1]{'period'},$_[1]{'resettime'},$_[1]{'begintime'},$_[1]{'end'},"\n");
	print $f $map."\n";
	print $f $trap."\n";
	close($f);
}

sub save_log{
	my($text,$file,@tmp);
	$text=$_[1];
	open(my $f,">$mesafile");
	for($i=0;$i<@{$$text{'all'}} && $maxalllog;$i++){
		print $f $$text{'all'}[$i]."\n";
	}
	close($f);
	open(my $f,">$mescfile");
	for($i=0;$i<@cname;$i++){
		print $f $$text{'housin'}[$i]."\n";
	}
	for($i=0;$i<@{$$text{'country'}} && $i<$maxcountrylog;$i++){
		print $f $$text{'country'}[$i]."\n";
	}
	close($f);
	open(my $f,">$actsfile");
	for($i=0;$i<@{$$text{'action'}} && $i<$maxactionlog;$i++){
		print $f $$text{'action'}[$i]."\n";
	}
	close($f);
	open(my $f,">$histfile");
	for($i=0;$i<@{$$text{'history'}} && $i<$maxhistorylog;$i++){
		print $f $$text{'history'}[$i]."\n";
	}
	close($f);
}

# 新規登録
sub action_new{
	my($i,$c,$ppls,$pset,$pmap,$plog,$dt,@cnum,%dt);
	($ppls,$plog,$pset,$pmap)=@_;
	for($i=0;$i<@{$$ppls{'pls'}};$i++){
		if($$ppls{'pls'}[$i]{'name'} eq $form{'gnm'}){
			&error('新規登録エラー：「'.$form{'gnm'}.'」同じ名前で既に登録されています');
		}
		$cnum[$$ppls{'pls'}[$i]{'belong'}]++;
	}
	$c=0;
	for($i=1;$i<@cname;$i++){
		$c=$i if $$pset{'country'}[$i] && (!$c || $cnum[$c]>$cnum[$i]);
	}
	$dt{'name'}=$form{'gnm'};
	$dt{'pass'}=&pass($form{'gpw'});
	$dt{'belong'}=$c;
	$dt{'origin'}=$c;
	$dt{'item'}=[];
	$dt{'posi'}=&defaultpt($c);
	$dt{'wait'}=0;
	$dt{'wamax'}=$firstwait;
	$dt{'move'}=$firstmove;
	$dt{'mvmax'}=$firstmove;
	$dt{'point'}=0;
	$dt{'lastlogin'}=time;
	$dt{'honor'}=0;
	$dt{'status'}=[0,0,0,0,0];
	$dt{'itemflags'}=[];
	$dt{'actflag'}=0;
	$dt{'config'}='';
	$dt{'board'}='';
	$$ppls{'id'}=@{$$ppls{'pls'}};
	push(@{$$ppls{'pls'}},&transpl(\%dt));
	$$pmap[$dt{'posi'}]{'member'}[$dt{'belong'}]++;
	unshift(@{$$plog{'action'}},&printtime(time).sprintf(' <span class=B%s><B>%s</B>が志願兵として<B>%s</B>に入国しました。</span><br>',$c,$dt{'name'},$cname[$c]));
}

sub reset{
	my($c,$ppls,$pmap,$plog,$pset,$newmap,$stockmap,$shuffle,@pls);
	($ppls,$pmap,$plog,$pset)=@_;
	open(F,$stockfile);$newmap=<F>;while(<F>){$stockmap.=$_;}close(F);
	open(F,">$stockfile");print F $stockmap;close(F);
	chomp($newmap);
	if($newmap eq ''){$$pset{'resettime'}+=$beginwait;$$pset{'begintime'}+=$beginwait;return;}
	@{$$pset{'country'}}=();
	$c=0;foreach(split(//,$newmap)){
		$$pmap[$c]=&getmap($_);
		$$pset{'country'}[$$pmap[$c]{'belong'}]++ if $$pmap[$c]{'ownable'};
		$c++;
	}
	$shuffle='<table class=shuffle><colgroup>';
	for($c=1;$c<@cname;$c++){$shuffle.="<col class=B$c>";}
	$shuffle.='</colgroup><tr>';
	for($c=1;$c<@cname;$c++){$shuffle.="<th>$cname[$c]</th>";}
	@pls=@{$$ppls{'pls'}};
	for($c=0;$c<@pls;$c++){my $i=rand(@pls-$c)+$c;@pls[$i,$c]=@pls[$c,$i] if $i!=$c;}
	$c=0;foreach(@pls){
		$$_{'belong'}=$c%$#cname+1;
		$$_{'origin'}=$$_{'belong'};
		$$_{'posi'}=&defaultpt($$_{'belong'});
		$$_{'actflag'}=0;
		$$_{'status'}[4]++;
		$$pmap[$$_{'posi'}]{'member'}[$$_{'belong'}]++;
		$shuffle.="</tr><tr>" if $$_{'belong'}==1;
		$shuffle.="<td>$$_{'name'}</td>";
		$c++;
	}
	while($c++%$#cname){$shuffle.='<td></td>';}
	$shuffle.='</tr></table>';
	@{$$plog{'country'}}=();
	@{$$plog{'housin'}}=();
	unshift(@{$$plog{'action'}},&printtime(time).' <b>…そして新たなる史実が幕を開ける</b><br>'.$shuffle);
	$$pset{'period'}++;
	$$pset{'end'}=0;
}

# 移動位置計算
sub movept{
	my($dir,$posi);
	$dir=$_[0];$posi=$_[1];
	if($dir==0 && $posi>=$width){$posi-=$width;}
	if($dir==1 && $posi%$width>0){$posi--;}
	if($dir==2 && $posi%$width+1<$width){$posi++;}
	if($dir==3 && $posi<($width-1)*$height){$posi+=$width;}
	return $posi;
}

# 初期位置
sub defaultpt{
	my($cid,$posi);
	$cid=$_[0];
	if($cid==1){return $width+1;}
	if($cid==2){return $width*2-2;}
	if($cid==3){return ($height-2)*$width+1;}
	if($cid==4){return ($height-1)*$width-2;}
	return $width*$height;
}

# 攻撃力 防御力
sub calcbattle{
	my($pl,$map,$pls,$flag,$atkable,$mynm,$vsnm,$mytxt,$vstxt,@add);
	($flag,$posi,$pl,$map,$pls)=@_;
	$mynm=$$map[$posi]{'member'}[$$pl{'belong'}];
	$vsnm=$$map[$posi]{'member'}[$$map[$posi]{'belong'}];
	$mytxt=$mynm.'人';
	$vstxt=$vsnm.'人';
	for(0..3){
		my $tposi=&movept($_,$posi);
		if($$map[$tposi]{'belong'}==$$pl{'belong'}){$atkable=1;}
		if($$pl{'itemflags'}[2]>0 && $flag&2){$add[1]+=$$map[$tposi]{'member'}[$$pl{'belong'}]*$items[1]{'val'};}
	}
	if($$pl{'itemflags'}[1]>0 && $flag&1){$add[0]+=$items[0]{'val'};}
	foreach(@add){if($_ ne ''){$mynm+=$_;$mytxt.="+$_";}}
	return($atkable,$mynm,$mytxt,$vsnm,$vstxt);
}

sub getmap{
	my($p,$land,$trap,$member);
	$land=$_[0];$trap=$_[1];$member=$_[2]?$_[2]:[];
	$$p={
		'land',$land,
		'trap',$trap,
		'member',$member,
		'name',$lname[$land],
		'cost',$land==6?2:$land==8?3:$land==5?0:1,
		'hp',$land==7?5:0,
		'movable',$land==9?0:1,
		'belong',$land<@cname?$land:0,
		'ownable',$land<@cname?1:0,
	};
}

sub transpl{
	my($p);
	$p=$_[0];
	$$p{'ptmax'}=$$p{'mvmax'}>$pointmax?$pointmax:$$p{'mvmax'};
	$$p{'logcond'}={'all',3,'country',10,'action',30,'history',3};
	$$p{'score'}=int(($$p{'status'}[0]*100+$$p{'status'}[1]*10-$$p{'status'}[2]*5+$$p{'status'}[3])/($$p{'status'}[4]/2+4));
	return $p;
}

# 暗号化
sub pass{return crypt($_[0],'gn');}

sub printpl{
	return &printcn($_[0]{'belong'},$_[0]{'name'});
}
sub printcn{
	my($country,$text)=@_;
	return "<span class=B$country>$text</span>";
}

sub printpt{
	my($land,$posi,$text);
	($land,$posi)=@_;
	$text=sprintf('(%d,%d)',$posi%$width,int($posi/$width));
	return $land eq ''?$text:&printmp($land,$text);
}

sub printmp{
	my($land,$text)=@_;
	return "<span class=B$land>$text</span>";
}

# 時刻表示
sub printtime{
	my($return,@time);
	@time=localtime($_[0]);
	$time[4]++;
	$time[5]+=1900;
	return sprintf("%d/%02d/%02d %02d:%02d:%02d",$time[5],$time[4],$time[3],$time[2],$time[1],$time[0]);
}

#---------------------------------------------------------------

sub action_admin{
	my($count);
	print &header();
		print << "-HTML-";
<form action="$cgi" method=POST>
<input type=hidden name=mode value=admin>
-HTML-
	if($form{'pass'} eq ''){
		print << "-HTML-";
pass<input type=text name=pass><br>
<input type=submit value='ログイン'>
</form>
-HTML-
		print &footer();
		return;
	}
	if($form{'pass'} ne $adminpass){
		print 'error</form>';
		print &footer();
		return;
	}
	if($form{'cmd'} eq 'mapedit'){
		my($set,$map,$log,$po,$pn,$posi);
		($set,$map)=&load_map(undef);
		($log)=&load_log(undef);
		$pn=&getmap($form{'land'});
		$posi=$form{'posi'};
		unshift(@{$$log{'action'}},&printtime(time).' '.&printpt($$map[$posi]{'land'},$posi).sprintf("が<span class=B%s>%s</span>から<span class=B%s>%s</span>に変更されました。<br>",$$map[$posi]{'land'},$$map[$posi]{'name'},$$pn{'land'},$$pn{'name'}));
		$$map[$posi]=$pn;
		&save_map(undef,$set,$map);
		&save_log(undef,$log);
		print "マップ編集完了。\n";
	} elsif ($form{'cmd'} eq 'reset'){
		my($ppls,$log,$set,$map);
		$ppls=&load_pls(undef);
		($pset,$pmap)=&load_map(undef,$$ppls{'pls'});
		$plog=&load_log(undef);
		&reset($ppls,$pmap,$plog,$pset);
		$$pset{'begintime'}=time+$beginwait;
		&save_pls(undef,$ppls);
		&save_map(undef,$pset,$pmap);
		&save_log(undef,$plog);
		print "リセット完了。\n";
	}
	if($form{'cmd'} eq 'mapcreate'){
		if(length($form{'map'})==$width*$height){
			open(F,">>$stockfile");print F $form{'map'}."\n";close(F);
			print "マップ登録完了。\n";
		}else{
			print 'マップの規定字数ではありません。'.length($form{'map'})."!=".int($width*$height)."\n";
		}
	}
	$count=0;
	open(F,$stockfile);while(<F>){$count++;}close(F);
	print << "-HTML-";
<input type=hidden name=cmd>
<input type=hidden name=pass value="$form{'pass'}">
<hr>
<h3>マップ登録</h3>
ストック $count個<br>
<input type=text name=map size=99><br>
<input type=submit value='送信' onclick='this.form.cmd.value="mapcreate"'>
<hr>
<h3>地形変更</h3>
場所ID<input type=text name=posi size=4><br>
地形ID<input type=text name=land size=2><br>
<input type=submit value='送信' onclick='this.form.cmd.value="mapedit"'>
<hr>
<h3>強制リセット</h3>
<input type=submit value='送信' onclick='this.form.cmd.value="reset"'>
-HTML-
	print &footer();
}

#---------------------------------------------------------------

sub header{
	my($date,%param);
	%param=%{$_[0]};
	$date=&printtime(time);
	$return.="Set-Cookie:gannar=;expires=Sun ,".sprintf("%02d",$gmt[3])."-".('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec')[$gmt[4]]."-$gmt[5] 00:00:00 GMT\n";
	$return.="Content-type:text/html;\n\n";
	$return.=<< "-HEAD-";
<HTML lang='ja-JP'><HEAD><META NAME='ROBOTS' CONTENT='INDEX,FOLLOW'>
<META HTTP-EQUIV='Content-type' CONTENT='text/html; charset=Shift_JIS'>
<META NAME='description' CONTENT='非同期式多人数同時参加対戦型オンライン陣取りゲーム。他国同盟や全50種類のアイテムによる戦略的戦術的駆け引きを駆使し、全土統一せよ。'>
<META NAME='keywords' CONTENT='SSDI,CGI,オンライン,携帯,ブラウザ,無料,シミュレーション'>
<META NAME='Author' CONTENT='Darselle'>
<LINK REL='STYLESHEET' TYPE='text/css' HREF='http://cgi28.plala.or.jp/ssdi/gannar/designw.css' TITLE='デザイン'>
<TITLE>$title</TITLE>
<style>
body{background:$bgcolor;color:$textcolor;}
div.title{background:#AAFFAA;margin:3px;padding:1px;}
div.firstlink{background:#AAFFAA;margin:3px;padding:1px;}
#map{font-size:90%;text-align:center;border-collapse:collapse;border:1px solid black;width:auto;}
#map td{padding:0px;}
#map .outer,#map .outer td{border:1px solid black;}
h2{background:#AAFFAA;margin:3px;font-size:100%;font-weight:normal;padding:1px;}
h3{font-size:100%;margin:0px;font-weight:normal;}
.footlink{text-align:center;}
.copy{text-align:center;}
table{width:100%;}
.shuffle{border:1px solid black;border-collapse:collapse;}
.shuffle td{border:1px solid black;}
.direct{width:auto;}
$param{'css'}
</style>
$param{'head'}
</HEAD>
<BODY BGCOLOR='$bgcolor'>
<div class="title B$param{'cid'}"><B class=title>$title</B> 【$date】【参加人数：$param{'pltotal'}人】【ログイン中：約$param{'plnow'}人】</div>
-HEAD-
	return $return;
}

sub footer{
	print "<hr>".&dump(\%form);
	return << "-FOOT-";
<HR><div class=footlink><a href='$cgi'>$title 初期画面へ</a></div>
<HR><div class=copy>原案：<A HREF='http://game1.openspc2.org/~ssdi/'>All Rights Reserved,(C)ガンナー & はやぶさ LIMITED 2006-2013</A></DIV>
<HR><div class=copy>作成：<A HREF='http://csyuki.sakura.ne.jp/'>Darselle</A></DIV>
</BODY></HTML>
-FOOT-
}

sub error{
	print "Content-type:text/html;\n\n";
	print << "-HTML-";
<HTML><HEAD><META NAME='ROBOTS' CONTENT='NOINDEX,FOLLOW'>
<META http-equiv='content-type' content='text/html; charset=Shift_JIS'>
<TITLE>$title -Error</TITLE></HEAD>

<BODY BGCOLOR='$bgcolor'><DIV ALIGN='center'><H3>問題が発生しています。</H3>
<div style='color:red'><B>Error:</B> <U>$_[0]</U></div><BR>
<HR><A HREF='./$cgi'>ガンナー 初期画面に戻る</A><BR>
<FONT COLOR='#888888'>注意：ボタンの連打はキャラクターの消失につながります</FONT>
</DIV></BODY></HTML>
-HTML-
	print "<hr>".&dump(\%form);
	&unlock();
	exit 1;
}

sub lock{
	my $retry=0;my $wait=10;my $wait2=3;
	$txtx="";
	if(-e $lock && time>(stat($lock))[9]+$wait){
		if(time>(stat($lock."2"))[9]+$wait2){rmdir $lock."2";}
		if(mkdir($lock."2")){rmdir $lock;}
		$txtx.="&";
	}
	while(!mkdir($lock,755)){select(undef,undef,undef,0.2);if($retry++>5){&error('ロックエラー');return 1;}}
	return 0;
}
sub unlock{rmdir $lock;}

#################################
sub dump{
	my($ret);$ret="";
	$ret.="!(" if @_>1;
	foreach(@_){#last if $exitsts++>9999;
		if(ref $_ eq 'HASH'){my %h=%$_;$ret.="{".join(",",map{$_."=".&dump($h{$_})}sort keys %h)."},";}
		elsif(ref $_ eq 'ARRAY'){$ret.="(".join(",",map{&dump($_)}@$_)."),";}
		elsif(ref $_ eq 'SCALAR'){$ret.="".$$_.",";}
		else{$ret.="$_,";}
	}
	$ret=substr($ret,0,-1);
	$ret.=")" if @_>1;
	return $ret;
}

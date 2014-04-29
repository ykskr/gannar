#!/usr/bin/env perl

#------ option start -------#

$cgi='gannar.cgi';
$adminpass='******';

@cname=('Gray','Red','Green','Blue','Yellow');
@lname=('�D','��','��','��','��','��','�X','��','��','�R');
$width=30;# �}�b�v����
$height=30;# �}�b�v�c��
$firstmove=10;# �����ړ���
$movemax=20;# �ő�ړ���
$firstwait=180;# �����񕜊Ԋu
$waitmin=450;# �񕜊Ԋu�ŏ�
$waitadd=10;# �񕜊Ԋu���Z
$waitmax=600;# �񕜊Ԋu�ő�
$pointmax=15;# ���M�ő�
$cntrythre=3;# �ŏ��̓y
$ruinpoint=10;# �ŖS�{�l���M
$ruinptpoint=3;# �ŖS�������M
$resetwait=43200;# ���ꂩ�烊�Z�b�g�܂ŕb��
$beginwait=43200;# ���Z�b�g����J�n�܂ŕb��

$logintime=600;# ���O�C�����Ƃ݂Ȃ��b��

$maxalllog=100;# �S�̃��O
$maxcountrylog=500;# �����O
$maxactionlog=500;# �s�����O
$maxhistorylog=999999;# ���j���O

@deletecount=([14,0],[7,20],[3,1]);

$title='�K���i�[(�R�s�[)';# �^�C�g��
$bgcolor='#EEFFEE';# �w�i�F
$textcolor='black';# �����F

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
	{'name','������','order',0,'gettype',0,'max',9,'val',1,'fid',1,'time',3600,'ename','�U����Up',},
	{'name','���R��','order',1,'gettype',0,'max',9,'val',0.3,'fid',2,'time',3600,'ename','�e����Up',},
	{'name','�h�{��','order',2,'gettype',0,'max',9,'val',10,'fid',3,'time',3600,'ename','�h�{��NG',},
	{'name','�|�S��','order',4,'gettype',0,'max',9,'need',2,},
	{'name','�@��@','order',5,'gettype',0,'max',9,'need',4,},
	{'name','�y����','order',6,'gettype',0,'max',9,'need',7,},
	{'name','�m�Ԑ�','order',3,'gettype',0,'max',9,},
	{'name','�o�ዾ','order',7,'gettype',0,'max',9,'val',1,},
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

# TOP���
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
<h2 class=oldmap><B>�ߋ��n�`�{�� ��</B></h2>
<FORM ACTION='$cgi' method='POST' NAME='gannar'>
<SELECT NAME=val><OPTION VALUE=0>�Ȃ�
</SELECT><INPUT TYPE=hidden NAME=mode VALUE='old'>
<INPUT TYPE='submit' VALUE='�ߋ��̒n�`�m�F'>
</FORM>
-HTML-
	$ret .= "<div class=firstlink>".&printlink()."</div>\n";
	$ret .= << "-HTML-";
<FORM ACTION='$cgi' method='POST' NAME='gannar' class=login>
<B>�Q���Җ�</B><INPUT TYPE='text' SIZE='18' NAME='gnm' VALUE='' MAXLENGTH='20'><BR>
<B>�p�X���[�h</B><INPUT TYPE='password' SIZE='10' NAME='gpw' MAXLENGTH='16'>
<input type=hidden name=mode value=login>
<INPUT TYPE='submit' VALUE='���O�C��'></FORM>
-HTML-
	$ret .= << "-HTML-";
<FORM ACTION='$cgi' method='POST' NAME='gannar' class=login>
<B>�Q���Җ�</B><INPUT TYPE='text' SIZE='18' NAME='gnm' VALUE='' MAXLENGTH='20'><BR>
<B>�p�X���[�h</B><INPUT TYPE='password' SIZE='10' NAME='gpw' MAXLENGTH='16'>
<input type=hidden name=mode value=new>
<INPUT TYPE='submit' VALUE='�V�K�o�^'></FORM>
-HTML-
	$ret .= &printlog($plog,{'logcond',{'all',3,'country',10,'action',30,'history',3}});
	$ret .= &footer();

	return $ret;
}

# ���C�����
sub action_main{
	my($pset,$pmap,$ppls,$plog,$pl,$logcond,$message);
	($ppls,$plog,$pset,$pmap)=@_;
	$pl=$$ppls{'pls'}[$$ppls{'id'}];
	if($$pl{'name'} ne $form{'gnm'}){
		&error('���O�C�����G���[�F���̖��O�͑��݂��܂���('.$form{'gnm'}.')');
	}elsif($$pl{'pass'} ne &pass($form{'gpw'})){
		&error('���O�C�����G���[�F�p�X���[�h���Ⴂ�܂�('.$form{'gpw'}.')');
	}

	if((!-e $mapsfile || $$pset{'end'}) && $$pset{'resettime'}<time){
		&reset($ppls,$pmap,$plog,$pset);
	}

	for($i=0;$i<@{$$ppls{'pls'}};$i++){
		next if $i==$$ppls{'id'};
		foreach(@deletecount){
			if($$ppls{'pls'}[$i]{'lastlogin'}+$$_[0]*86400<time && (!$$_[1] || $$ppls{'pls'}[$i]{'status'}[4]<$$_[1])){
				$txt=&printpl($$ppls{'pls'}[$i]).' [����'.$$ppls{'pls'}[$i]{'status'}[0].'/�J��'.$$ppls{'pls'}[$i]{'status'}[3].'/�]��'.$$ppls{'pls'}[$i]{'status'}[4].'] ��'.$$_[0].'���ȏ����A���������̂ŏ��������ƂȂ�܂���';
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
		$message.='�ړ��͂�'.$heal.'�񕜂��܂����B<br>' if $heal>0;
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
			$message.='�p�X���[�h��ύX���܂����B<br>';
		}
	}elsif($form{'mode'} eq 'looking'){
		if($form{'val'}==1){$message.=&players($ppls,$pmap,$pl);}
		elsif($form{'val'}==2){$$pl{'logcond'}{'all'}=0;}
		elsif($form{'val'}==3){$$pl{'logcond'}{'country'}=0;}
		elsif($form{'val'}==4){$$pl{'logcond'}{'action'}=0;}
		elsif($form{'val'}==5){$$pl{'logcond'}{'history'}=0;}
		elsif($form{'val'}==6){$message.=&ranking($ppls,$pl);}
		elsif($form{'val'}==8){$message.="�������ł��B";}
		elsif($form{'val'}==9){$message.=&config($pl);}
	}elsif($form{'mode'} eq 'shout'){
		$message.=&comment($pl,$plog,$form{'mes'},$form{'val'});
	}elsif($$pset{'begintime'}>time){
		$message.='�܂��n�܂��Ă��܂���B<br>�J�n�܂ł��҂����������B<br>';
	}elsif($form{'dir'}){
		if($$pl{'move'}>0){$message.=&move($form{'dir'},$$ppls{'pls'},$pl,$pmap,$plog,$pset);}
		else{$message.="�ړ��͂�����܂���B<br>";}
	}elsif($form{'mode'} eq 'card'){
		$message.=&item($$ppls{'pls'},$pl,$pmap,$plog,$pset,$form{'val'});
	}

	while($$pl{'point'}>=$$pl{'ptmax'}){
		$$pl{'point'}-=$$pl{'ptmax'};
		$$pl{'status'}[3]++;
		$message.="���M��$$pl{'ptmax'}�𒴂������߁A�e��J�܂��󂯎��܂��B<br>\n";
		foreach(sort{$items[$a]{'order'}<=>$items[$b]{'order'}}(0..$#items)){
			if($items[$_]{'gettype'}==0 && $$pl{'item'}[$_]<$items[$_]{'max'}){
				$message.='<b>'.$items[$_]{'name'}.'</b>����肵�܂����B<br>';
				$$pl{'item'}[$_]++;
			}
		}
	}

	print "<h2><b>���̕��j</b> $$plog{'housin'}[$$pl{'belong'}]</h2>" if $$plog{'housin'}[$$pl{'belong'}] ne '';
	print &printfield($pset);
	print "<table><tr><td valign=top>\n";
	print &printmap({'map',$pmap,'pl',$pl});
	print "</td><td valign=top>\n";
	print &status($pl,$$pmap[$$pl{'posi'}]{'land'});
	print &command($pl,$$pset{'begintime'});
	print "</td></tr></table>\n";
	print "<h2><B>�l���O</B></h2>\n$message\n" if $message ne '';
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
		$ret .= "<td valign=top><div class=num>$cnm[$i]�l</div>\n$cntry[$i]\n</td>\n" if $cntry[$i];
	}
	$ret .= "</tr></table>\n";
	$ret .= &footer();
}

#---------------------------------------------------------------

# �ړ�
sub move{
	my($dir,$dirtxt,$pl,$pls,$map,$log,$posi,$return,$atkable,$txt,$enemy,$ruinflag);
	($dirtxt,$pls,$pl,$map,$log,$setting)=@_;
	$dir=$_[0] eq '�k'?0:$_[0] eq '��'?1:$_[0] eq '��'?2:3;
	$posi=$$pl{'posi'};
	$$map[$$pl{'posi'}]{'arrow'}=('��','��','��','��')[$dir];
	while($posi==$$pl{'posi'} || !$$map[$posi]{'cost'}){
		$return.="$$map[$posi]{'name'}�n�`�̂��߁A����ɑO�i���܂����B<br>" if $posi!=$$pl{'posi'};
		$tposi=&movept($dir,$posi);
		if($tposi==$posi){return "$return�ړ����悤�Ƃ��܂������A�ړ��悪�[�����̂��ߎ��s���܂����B<br>";}
		if(!$$map[$tposi]{'movable'}){return $return.'�ړ����悤�Ƃ��܂������A�ړ���'.&printpt('',$tposi).'��'.&printmp($$map[$tposi]{'land'},$$map[$tposi]{'name'}).'�̂��ߎ��s���܂����B<br>';}
		if($$map[$tposi]{'cost'}>$$pl{'move'}){return $return.'�ړ����悤�Ƃ��܂������A�ړ���'.&printpt('',$posi).'��'.&printmp($$map[$tposi]{'land'},$$map[$tposi]{'name'}).'�̂��߈ړ��͂�����܂���B<br>';}
		$posi=$tposi;
	}
	$return.=&printpt($$map[$$pl{'posi'}]{'land'},$$pl{'posi'}).'����'.&printpt($$map[$posi]{'land'},$posi).'�ֈړ����܂����B<br>';
	if($$map[$posi]{'cost'}>1){$return.=$$map[$posi]{'name'}.'�n�`�̂��߁A�ړ��͂�'.$$map[$posi]{'cost'}.'����܂��B<br>';}
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
	$txt=&printpl($pl).'��'.&printpt($$map[$posi]{'land'},$posi).'�ɂ�'.&printcn($$pl{'belong'},"$mytxt").'��'.&printmp($$map[$posi]{'land'},$$map[$posi]{'name'});
	if($$map[$posi]{'hp'}>$mynm){
		$txt.='���󂻂��Ƃ��܂��������s���܂����B<br>';
	}else{
		$txt.='��j�󂵂܂����B<br>';
		$$map[$posi]{'land'}=$$pl{'belong'};
		$$map[$posi]{'belong'}=$$pl{'belong'};
	}
	$return.=$txt;
	unshift(@{$$log{'action'}},&printtime(time).' '.$txt);
	return $return;
}

# ���
sub battle{
	my($dir,$dirtxt,$pl,$pls,$map,$log,$posi,$return,$atkable,$txt,$enemy,$ruinflag,$mynm,$mytxt,$vsnm,$vstxt);
	($dirtxt,$pls,$pl,$map,$log,$setting,$posi)=@_;
	($atkable,$mynm,$mytxt,$vsnm,$vstxt)=&calcbattle(3,$posi,$pl,$map,$pls);
	return if !$atkable;
	$return.=&printpt($$map[$posi]{'land'},$posi).'�ɐ�̍s�ׂ����{���܂��B<br>';
	$enemy=$$map[$posi]{'belong'};
	$txt=&printpl($pl).' �� '.&printpt($$map[$posi]{'land'},$posi);
	if($vsnm){
		$txt.=sprintf('�ɂ�<span class=B%s>%s</span>VS<span class=B%s>%s</span>�̑�����',$$pl{'belong'},$mytxt,$enemy,$vstxt);
	}else{
		$txt.='��';
	}
	if($mynm>$vsnm){
		$txt.='��������' if $vsnm;
		$txt.='��̂��܂����B<br>';
		$return.=$txt;
		if($$pl{'wamax'}>$waitmin){
			$$pl{'wamax'}--;
			$return.='�񕜊Ԋu��1�������܂����B<br>';
		}
		if($vsnm>0){
			$$pl{'point'}++;
			$return.='���M��1�㏸���܂����B<br>';
		}
		$$setting{'country'}[$$pl{'belong'}]++;
		$$setting{'country'}[$enemy]--;
		if($$setting{'country'}[$enemy]<$cntrythre){$ruinflag=1;}
		elsif($enemy && $posi==&defaultpt($enemy)){$ruinflag=2;}
		$$map[$posi]{'land'}=$$pl{'belong'};
		$$map[$posi]{'belong'}=$$pl{'belong'};
	}else{
		$txt.='�s�k���܂����B<br>';
		$return.=$txt;
	}
	unshift(@{$$log{'action'}},&printtime(time).' '.$txt);
	if($ruinflag){
		$return.=&ruin($dirtxt,$pls,$pl,$map,$log,$setting,$enemy,$ruinflag);
	}
	return $return;
}

# �ŖS
sub ruin{
	my($dir,$dirtxt,$pl,$pls,$map,$log,$posi,$return,$atkable,$txt,$enemy,$ruinflag,$i);
	($dirtxt,$pls,$pl,$map,$log,$setting,$enemy,$ruinflag)=@_;
	unshift(@{$$log{'history'}},$$log{'action'}[0]);
	unshift(@{$$log{'action'}},&printtime(time).' '.sprintf('<span class=B%s>%s</span>��%s�A<span class=B%s><b>%s</b>(�̓y%d)</span>��<span class=B%s><b>%s</b>(�̓y%d)</span>��ŖS�����܂����B<br>',$$pl{'belong'},$$pl{'name'},("�̒n$cntrythre�����錾���s��","�{���n���ח�����")[$ruinflag-1],$$pl{'belong'},$cname[$$pl{'belong'}],$$setting{'country'}[$$pl{'belong'}],$enemy,$cname[$enemy],$$setting{'country'}[$enemy]));
	unshift(@{$$log{'history'}},$$log{'action'}[0]);
	unshift(@{$$log{'action'}},&printtime(time).' '.sprintf('<span class=B%s>%s</span>��<b class=B%s>%s</b>�̗̓y%d��S�ĒD�����܂����B<br>',$$pl{'belong'},$cname[$$pl{'belong'}],$enemy,$cname[$enemy],$$setting{'country'}[$enemy])) if $$setting{'country'}[$enemy];
	$return.="<span class=B$enemy>$cname[$enemy]</span>��ŖS�����܂����B<br>";
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
		unshift(@{$$log{'action'}},&printtime(time).' '.sprintf('<span class=B%s>%s</span>���瑽���̐l�ނ��S�����Ă����܂����B<br>',$enemy,$cname[$enemy])) if $enemy;
		for($i=0;$i<@tmp;$i++){$j=int rand(@tmp-$i)+$i;@tmp[$i,$j]=@tmp[$j,$i] if $i!=$j;}
		foreach(@tmp){
			foreach($i=0,$j=1;$j<@cname;$j++){$i=$j if $cnt[$j] && $j!=$enemy && (!$i || $cnt[$i]>$cnt[$j]);}
			$$_{'belong'}=$i;
			$$_{'posi'}=&defaultpt($i);
			$cnt[$i]++;
			$exl[$i].='�A' if $exl[$i];$exl[$i].=sprintf('<span class=B%s>%s</span>',$enemy,$$_{'name'});
		}
		for($i=1;$i<@exl;$i++){if($exl[$i]){
			unshift(@{$$log{'action'}},&printtime(time).' '.sprintf('<span class=B%s>%s</span>�ւ̖S���ҁF%s<br>',$i,$cname[$i],$exl[$i]));
		}}
	}else{
		$return.=&reign($dirtxt,$pls,$pl,$map,$log,$setting,$enemy,$ruinflag);
	}
	return $return;
}

# ����
sub reign{
	my($dir,$dirtxt,$pl,$pls,$map,$log,$posi,$return,$atkable,$txt,$enemy,$ruinflag,$i,$time,@tmp,@cnt);
	($dirtxt,$pls,$pl,$map,$log,$setting,$enemy,$ruinflag)=@_;
	$txt=sprintf('<span class=B%s>',$$pl{'belong'});
	$time=time-$$setting{'begintime'};
	if($time>3600){$txt.=sprintf('%d����%02d��',int($time/3600),int(($time%3600)/60+0.5));}
	else{$txt.=sprintf('%d��%02d�b��',int($time/60),$time%60);}
	$txt.='�̐헐�̖��A<b>'.$$pl{'name'}.'</b>���I��錾���s��<b>'.$cname[$$pl{'belong'}].'</b>�ɂ���'.$$setting{'period'}.'���S�y���ꂪ�����������܂���</span><br>';
	$return.='���ꂵ�܂����B<br>';
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

# �A�C�e��
sub item{
	my($dir,$dirtxt,$pl,$pls,$map,$log,$posi,$return,$atkable,$txt,$enemy,$ruinflag,$i,$time,@tmp,@cnt);
	($pls,$pl,$map,$log,$setting,$item)=@_;
	if($$pl{'item'}[$item]<=0){
		return $items[$item]{'name'}.'���g�p���悤�Ƃ��܂������A��������Ȃ����ߎ��s���܂����B<br>';
	}
	$txt='<b>'.$items[$item]{'name'}.'</b>���g�p���܂����B';
	unshift(@{$$log{'action'}},&printtime(time).' '.&printpl($pl).'��'.&printpt($$map[$$pl{'posi'}]{'land'},$$pl{'posi'}).'�ɂ�'.$txt);
	$return.=$txt.'<br>';
	$$pl{'item'}[$item]--;
	if($item==0){
		$return.='�U���͂�'.$items[$item]{'time'}.'�b�̊ԑ��������܂��B<br>';
		$$pl{'itemflags'}[$items[$item]{'fid'}]+=$items[$item]{'time'};
	}elsif($item==1){
		$return.='�e���͂�'.$items[$item]{'time'}.'�b�̊ԑ��������܂��B<br>';
		$$pl{'itemflags'}[$items[$item]{'fid'}]+=$items[$item]{'time'};
	}elsif($item==2){
		if($$pl{'itemflags'}[$items[$item]{'fid'}]>0){
			$$pl{'item'}[$item]++;
			shift(@{$$plog{'action'}});
			return '���̃A�C�e���̎g�p�͋֎~����Ă��܂��B�A�C�e���g�p�̓L�����Z������܂����B<br>';
		}else{
			$$pl{'move'}+=$items[$item]{'val'};
			$$pl{'itemflags'}[3]=$items[$item]{'time'};
			$return.='�ړ��͂�'.$items[$item]{'val'}.'�񕜂��܂����B<br>';
		}
	}elsif($item==3 || $item==4){
		if($$map[$$pl{'posi'}]{'belong'}!=$$pl{'belong'}){
			$txt='���ݒn�����w�łȂ����ߎ��s���܂����B';
		}elsif($$pl{'posi'}==&defaultpt($$pl{'belong'})){
			$txt='�{���n�̂��ߎ��s���܂����B';
		}else{
			$txt=$$map[$$pl{'posi'}]{'member'}[$$pl{'belong'}].'�l��';
			if($$map[$$pl{'posi'}]{'member'}[$$pl{'belong'}]<$items[$item]{'need'}){
				$txt.='�쐬���悤�Ƃ��܂������A�l��������Ȃ��������ߎ��s���܂����B';
			}else{
				$$map[$$pl{'posi'}]{'land'}=$item==3?7:8;
				$$map[$$pl{'posi'}]{'belong'}=0;
				$txt.=&printmp($$map[$$pl{'posi'}]{'land'},$lname[$$map[$$pl{'posi'}]{'land'}]).'���쐬���܂����B';
			}
		}
		$$log{'action'}[0].=$txt;
		$return.=$txt.'<br>';
	}elsif($item==5){
		if($$map[$$pl{'posi'}]{'land'}!=8){
			$txt='���ݒn��'.&printmp(8,$lname[8]).'�ł͂Ȃ����ߎ��s���܂����B';
		}else{
			$txt=$$map[$$pl{'posi'}]{'member'}[$$pl{'belong'}].'�l��';
			if($$map[$$pl{'posi'}]{'member'}[$$pl{'belong'}]<$items[$item]{'need'}){
				$txt.='���ߗ��Ă����s���܂������A�l��������Ȃ��������ߎ��s���܂����B';
			}else{
				$txt.=&printmp($$map[$$pl{'posi'}]{'land'},$$map[$$pl{'posi'}]{'name'}).'�̖��ߗ��Ăɐ������܂����B';
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
		$txt=&printpt($$map[$$pl{'posi'}]{'land'},$$pl{'posi'}).'�ւƃ����_�����[�v���܂����B';
		$$log{'action'}[0].=$txt;
		$return.=$txt.'<br>';
	}elsif($item==7){
		$return.='���ӂ̓G�̐l����㩂��m�F���܂��B<br>';
		for($i=0-$items[7]{'val'};$i<=$items[7]{'val'};$i++){
			next if $i*$width+$$pl{'posi'}<0 || $i*$width+$$pl{'posi'}>$height*$width;
			for($j=0-$items[7]{'val'};$j<=$items[7]{'val'};$j++){
				my($posi,$k,$txt);
				next if $$pl{'posi'}%$width+$j<0 || $$pl{'posi'}%$width+$j>$width;
				my $posi=$$pl{'posi'}+$i*$width+$j;
				my $k=0;
				foreach(@{$$map[$posi]{'member'}}){
					if($k!=$$pl{'belong'} && $_){
						$txt.=&printcn($k,$_.'�l');
						$$map[$posi]{'text'}.=&printcn($k,'<b style="color:red">'.$_.'</b>');
					}
					$k++;
				}
				$return.=&printpt($$map[$posi]{'belong'},$posi).$txt.'�A' if $txt;
			}
		}
		$return.='<br>';
	}
	$$log{'action'}[0].='<br>';
	return $return;
}

# ����/�`��
sub comment{
	my($pl,$text,$type,$typetxt,$return);
	$pl=$_[0];$log=$_[1];$txt=$_[2];$type=$_[3];
	return if $type!=2 && $txt eq '';
	return if $type==0;
	if($type==2){
		$$pl{'board'}=$txt;
		$return.=$txt eq ''?'�`������������悤��':"�u$txt�v<br>��";
		$return.="�{���n�ւƓ`�����B<br>";
	}elsif($type==3){
		$return.="�u$txt�v<br>�ƑS�̂Ɍ������ċ��񂾁B<br>";
		unshift(@{$$log{'all'}},&printtime(time)." <span class=B$$pl{'belong'}>$$pl{'name'}</span>:".$txt."<br>");
	}elsif($type==1){
		$return.="���̕��j���u$txt�v�ɕύX�����B";
		$$log{'housin'}[$$pl{'belong'}]=&printtime(time)." <span class=B$$pl{'belong'}>$$pl{'name'}</span>�F".$txt;
	}elsif($type==$$pl{'belong'}+10){
		$type-=10;
		$return.="�u$txt�v<br>�ƍ����p�����@�ɚ������B<br>";
		unshift(@{$$log{'country'}},&printtime(time)." <span class=B$$pl{'belong'}>$$pl{'name'}</span>�F".$txt."<br>&$type&$type&");
	}elsif($type<@cname+10){
		$type-=10;
		$return.="�u$txt�v<br>��$cname[$type]���ɓ`�����B<br>";
		unshift(@{$$log{'country'}},&printtime(time)." ".&printpl($pl)."��<span class=B$type>$cname[$type]</span>�F".$txt."<br>&$$pl{'belong'}&$type&");
	}
	return $return;
}

#---------------------------------------------------------------

# �^�C�g�������
sub printfield{
	my($i,$return,%param);
	%param=%{$_[0]};
	$return.="<h2 class=world><B>��$param{'period'}���嗤�󋵁@</B>";
	$return.="<span class=B4>".&printtime($param{'resettime'})."</span>��MAP�������B" if $param{'resettime'}>time;
	$return.="<span class=B4>".&printtime($param{'begintime'})."</span>�ɊJ�n���܂��B" if $param{'begintime'}>time;
	for($i=0;$i<@cname;$i++){
		$return.=" $cname[$i]�F$param{'country'}[$i]" if $param{'country'}[$i];
	}
	$return.="</h2>\n";
	return $return;
}

# �}�b�v�o��
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

# �`���\��
sub players{
	my($ppls,$map,$pl,$return);
	$ppls=$_[0];$map=$_[1];$pl=$_[2];
	$return=<< '-HTML-';
�����p�����@�ɂđS���̏��ݒn�Ɠ`�����m�F�����B<BR>
�y�Q���Җ�[�ړ���]�u�`�����e�v�z<BR>
���ŏI���O�C�����ԏ��ɕ\������Ă��܂�<BR>
��<B><U>10���ȓ��̃��O�C���҂͑����{����</U></B>�A<span class=B0>���s���҂͊D�F</span>�ŕ\�����Ă��܂�<BR>
��<U>�ꏊ������</U>�c�����Ɠ����ʒu�@�ړ��́c�ŏI���O�C�����̒l�@[�g��]�c�g�у��O�C���ҁ@[��]�c�]�����[��
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
		$return.="�u$$_{'board'}�v" if $$_{'board'} ne '';
		$return.='</span>' if !$$pl{'actflag'};
		$return.="<br>";
	}
	return $return;
}

# ���
sub ranking{
	my($ppls,$point,$ranktxt,$c,$i);
	$ppls=$_[0];$pl=$_[1];$c=1;$i=0;
	foreach(@{$$ppls{'pls'}}){$c++ if $$pl{'score'}<$$_{'score'};$i++ if $$pl{'score'}==$$_{'score'};}
	$ranktxt=$c.'��';
	$ranktxt.='�^�C(������'.$i.'�l)' if $i>1;
	return '<span style="color:red">����̌����F�@(����~�P�O�O�{�j��~�P�O�|�ŖS�~�T�{�J��) �� (�S�{�]�����Q)�@���؂�̂�</span><BR>�����@����̏��Ŏ������g�̐�����m�F�����B<BR><BR>���݂̐���� <B>'.$$pl{'score'}.'</B> �ł��B�S�Q����'.@{$$ppls{'pls'}}.'�l�� <B class=B4>'.$ranktxt.'</B>�ƂȂ��Ă��܂��B<br>'."\n";
}

# �ݒ�
sub config{
	my($pl);
	return << "-HTML-";
<form action='$cgi' method=POST>
<input type=hidden name=mode value=passchg>
<input type=hidden name=gnm value="$form{'gnm'}">
<input type=hidden name=gpw value="$form{'gpw'}">
<h3>�y�p�X���[�h��ύX����z</h3>
�V�p�X���[�h(4�`10��)�F<input type=password name=newpass>
<input type=submit value="�ύX">
</form>
-HTML-
}

# �X�e�[�^�X
sub status{
	my($pl,$posicn,$posi,$return);
	$pl=$_[0];
	$pointmax=15;
	$posi=&printpt($_[1],$$pl{'posi'});
	$return.=<< "-HTML-";
<h2><B>�X�e�[�^�X</B></h2>
<table>
<TR><TD VALIGN='top'><TABLE><TR><TH>�Q���Җ�</TH><TD COLSPAN=3>$$pl{'name'}</TD></TR>
<TR><TH>������</TH><TD><span class=B$$pl{'belong'}>$cname[$$pl{'belong'}]</span></TD><TH>���ꐔ</TH><TD>$$pl{'status'}[0]</TD></TR>
<TR><TH>�o�g��</TH><TD><span class=B$$pl{'origin'}>$cname[$$pl{'origin'}]</span></TD><TH>�j��</TH><TD>$$pl{'status'}[1]</TD></TR>
<TR><TH>���ݒn</TH><TD>$posi</TD><TH>�ŖS��</TH><TD>$$pl{'status'}[2]</TD></TR>
<TR><TH>���M</TH><TD>$$pl{'point'}/$$pl{'ptmax'}</TD><TH>�J�ܐ�</TH><TD>$$pl{'status'}[3]</TD></TR>
<TR><TH>�ړ���</TH><TD>$$pl{'move'}/$$pl{'mvmax'}</TD><TH>�]����</TH><TD>$$pl{'status'}[4]</TD></TR>
<TR><TH>�񕜊Ԋu</TH><TD COLSPAN=3>$$pl{'wait'}/$$pl{'wamax'}</TD></TR>
<TR><TH>�����l</TH><TD COLSPAN=3>$$pl{'honor'}</TD></TR>
-HTML-
	for($i=1;$i<@{$$pl{'itemflags'}};$i++){
		$return.="<tr><th>$items[$flagitem[$i]]{'ename'}</th><td colspan=3>�c��$$pl{'itemflags'}[$i]�b</td></tr>\n" if $$pl{'itemflags'}[$i];
	}
	$return.='<TR class=B0><TH>[���s��]</TH><TD COLSPAN=3>�e�퉶�b���ΏۊO</TD></TR>'."\n" if !$$pl{'actflag'};
	$return.="</table>\n</td></tr></table>\n";
	return $return;
}

# �R�}���h�\��
sub command{
	my($i,$pl,$begintime,$return,@tmp);
	$pl=$_[0];$begintime=$_[1];
	$pointmax=15;
	$return.=<< "-HTML-";
<h2><B>�R�}���h</B></h2>
<table><tr><td>
<BR>-�ړ�-<BR>
-HTML-
	$return.=<< "-HTML-" if time>$begintime;
<form ACTION="$cgi" method=POST>
<INPUT TYPE=hidden NAME=gnm VALUE='$form{'gnm'}'>
<INPUT TYPE=hidden NAME=gpw VALUE='$form{'gpw'}'>
<INPUT TYPE=hidden NAME=mode VALUE='move'>
<table class=direct><tr><td><td><input type=submit name='dir' value='�k'><td></tr>
<tr><td><input type=submit name='dir' value='��'><td><td><input type=submit name='dir' value='��'></tr>
<tr><td><td><input type=submit name='dir' value='��'><td></tr></table>
</form>
-HTML-
	$return.='�҂����Ԃ̂��߈ړ��o���܂���B<BR>�J�n���Ԃ܂ł��҂����������B<BR><BR>'."\n" if $begintime>time;
	$return.=<< "-HTML-";
</TD><TD ROWSPAN=2 VALIGN=top>
<FORM ACTION="$cgi" method=POST NAME=itemBox onSubmit='return funcSubmit()'><INPUT TYPE=hidden NAME=gnm VALUE='$form{'gnm'}'><INPUT TYPE=hidden NAME=gpw VALUE='$form{'gpw'}'><INPUT TYPE=hidden NAME=mode VALUE='card'>
-�A�C�e��-<BR>
<SELECT NAME='val'><OPTION VALUE='777'>--
-HTML-
	foreach(sort{$items[$a]{'order'}<=>$items[$b]{'order'}}(0..$#items)){
		$return.="<option value=$_>$items[$_]{'name'} $$pl{'item'}[$_]��\n" if $$pl{'item'}[$_];
	}
	$return.='</SELECT><BR>';
	$return.=$begintime>time?'�g�p�s��':"<INPUT TYPE=submit VALUE='�g�p'>\n";
	$return.=<< "-HTML-";
</FORM>
</TD></TR><TR><TD>
<FORM ACTION="$cgi" method=POST NAME=gannar><INPUT TYPE=hidden NAME=gnm VALUE='$form{'gnm'}'><INPUT TYPE=hidden NAME=gpw VALUE='$form{'gpw'}'><INPUT TYPE=hidden NAME=mode VALUE='looking'>
-�m�F-<BR><SELECT NAME=val><OPTION VALUE=1>�����̏ꏊ�Ɠ`��
<OPTION VALUE=8>�����̏�񃍃O
<OPTION VALUE=2>�S�Ă̑S�̔���
<OPTION VALUE=3>�S�Ă̍�������
<OPTION VALUE=4>�S�Ă̍s�����O
<OPTION VALUE=5>�S�Ă̗��j���O
<OPTION VALUE=6>�����̐��
<OPTION VALUE=9>�ݒ���
</SELECT><BR><INPUT TYPE=submit VALUE='�m�F'></FORM>
</TD></TR><TR><TD COLSPAN=2>
<FORM ACTION="$cgi" method=POST NAME=gannar><INPUT TYPE=hidden NAME=gnm VALUE='$form{'gnm'}'><INPUT TYPE=hidden NAME=gpw VALUE='$form{'gpw'}'><INPUT TYPE=hidden NAME=mode VALUE='shout'>
-����/�`��-<BR><INPUT TYPE=text NAME=mes SIZE=44 MAXLENGTH=300 VALUE=''><BR><SELECT NAME=val><OPTION VALUE=''>-----
-HTML-
	$return.=sprintf("<OPTION VALUE=%d>������\n",$$pl{'belong'}+10);
	$return.="<OPTION VALUE=3>�S�̂�\n";
	for($i=0;$i<@cname;$i++){
		$return.=sprintf("<OPTION VALUE=%d>%s��\n",$i+10,$cname[$i]) if $i!=$$pl{'belong'};
	}
	$return.=<< "-HTML-";
<OPTION VALUE=1>���̕��j
<OPTION VALUE=2>�`��
</SELECT><INPUT TYPE=submit VALUE='����/�X�V'></FORM></TD></TR>
</TABLE>
-HTML-
	return $return;
}

# ���O�\��
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
				$return.=$key eq 'all'?'�S�̔���':$key eq 'country'?'���ʔ���':$key eq 'action'?'�s�����O':$key eq 'history'?'���j���O':'�S��';
				$return.='</B>(';
				$return.=$$pl{'logcond'}{$key}?$$pl{'logcond'}{$key}:'�S';
				$return.='���\��)</h2>'."\n";
			}
			$return.=$txt."\n";
			$c++;
		}
	}
	return $return;
}

# �����N�\��
sub printlink{
	return << "-HTML-";
<s HREF='./regist.html'>�V�K�o�^</s> , <s HREF='./manual.html'>������</s> , <s HREF='./question.html'>Q&A</s> , <A HREF='$cgi?mode=playerlist'>����</A> , <s HREF='./version.html'>�d�l�ύX����(616��)</s> , <s HREF='./link.html'>Link</s> , <A HREF='$bbsurl'>�f����</A> , <A HREF='$chaturl'>�`���b�g</A>
-HTML-
}

#---------------------------------------------------------------

# �e��ǂݍ���
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

# �e��ۑ�
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

# �V�K�o�^
sub action_new{
	my($i,$c,$ppls,$pset,$pmap,$plog,$dt,@cnum,%dt);
	($ppls,$plog,$pset,$pmap)=@_;
	for($i=0;$i<@{$$ppls{'pls'}};$i++){
		if($$ppls{'pls'}[$i]{'name'} eq $form{'gnm'}){
			&error('�V�K�o�^�G���[�F�u'.$form{'gnm'}.'�v�������O�Ŋ��ɓo�^����Ă��܂�');
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
	unshift(@{$$plog{'action'}},&printtime(time).sprintf(' <span class=B%s><B>%s</B>���u�蕺�Ƃ���<B>%s</B>�ɓ������܂����B</span><br>',$c,$dt{'name'},$cname[$c]));
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
	unshift(@{$$plog{'action'}},&printtime(time).' <b>�c�����ĐV���Ȃ�j���������J����</b><br>'.$shuffle);
	$$pset{'period'}++;
	$$pset{'end'}=0;
}

# �ړ��ʒu�v�Z
sub movept{
	my($dir,$posi);
	$dir=$_[0];$posi=$_[1];
	if($dir==0 && $posi>=$width){$posi-=$width;}
	if($dir==1 && $posi%$width>0){$posi--;}
	if($dir==2 && $posi%$width+1<$width){$posi++;}
	if($dir==3 && $posi<($width-1)*$height){$posi+=$width;}
	return $posi;
}

# �����ʒu
sub defaultpt{
	my($cid,$posi);
	$cid=$_[0];
	if($cid==1){return $width+1;}
	if($cid==2){return $width*2-2;}
	if($cid==3){return ($height-2)*$width+1;}
	if($cid==4){return ($height-1)*$width-2;}
	return $width*$height;
}

# �U���� �h���
sub calcbattle{
	my($pl,$map,$pls,$flag,$atkable,$mynm,$vsnm,$mytxt,$vstxt,@add);
	($flag,$posi,$pl,$map,$pls)=@_;
	$mynm=$$map[$posi]{'member'}[$$pl{'belong'}];
	$vsnm=$$map[$posi]{'member'}[$$map[$posi]{'belong'}];
	$mytxt=$mynm.'�l';
	$vstxt=$vsnm.'�l';
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

# �Í���
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

# �����\��
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
<input type=submit value='���O�C��'>
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
		unshift(@{$$log{'action'}},&printtime(time).' '.&printpt($$map[$posi]{'land'},$posi).sprintf("��<span class=B%s>%s</span>����<span class=B%s>%s</span>�ɕύX����܂����B<br>",$$map[$posi]{'land'},$$map[$posi]{'name'},$$pn{'land'},$$pn{'name'}));
		$$map[$posi]=$pn;
		&save_map(undef,$set,$map);
		&save_log(undef,$log);
		print "�}�b�v�ҏW�����B\n";
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
		print "���Z�b�g�����B\n";
	}
	if($form{'cmd'} eq 'mapcreate'){
		if(length($form{'map'})==$width*$height){
			open(F,">>$stockfile");print F $form{'map'}."\n";close(F);
			print "�}�b�v�o�^�����B\n";
		}else{
			print '�}�b�v�̋K�莚���ł͂���܂���B'.length($form{'map'})."!=".int($width*$height)."\n";
		}
	}
	$count=0;
	open(F,$stockfile);while(<F>){$count++;}close(F);
	print << "-HTML-";
<input type=hidden name=cmd>
<input type=hidden name=pass value="$form{'pass'}">
<hr>
<h3>�}�b�v�o�^</h3>
�X�g�b�N $count��<br>
<input type=text name=map size=99><br>
<input type=submit value='���M' onclick='this.form.cmd.value="mapcreate"'>
<hr>
<h3>�n�`�ύX</h3>
�ꏊID<input type=text name=posi size=4><br>
�n�`ID<input type=text name=land size=2><br>
<input type=submit value='���M' onclick='this.form.cmd.value="mapedit"'>
<hr>
<h3>�������Z�b�g</h3>
<input type=submit value='���M' onclick='this.form.cmd.value="reset"'>
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
<META NAME='description' CONTENT='�񓯊������l�������Q���ΐ�^�I�����C���w���Q�[���B����������S50��ނ̃A�C�e���ɂ��헪�I��p�I�삯��������g���A�S�y���ꂹ��B'>
<META NAME='keywords' CONTENT='SSDI,CGI,�I�����C��,�g��,�u���E�U,����,�V�~�����[�V����'>
<META NAME='Author' CONTENT='Darselle'>
<LINK REL='STYLESHEET' TYPE='text/css' HREF='http://cgi28.plala.or.jp/ssdi/gannar/designw.css' TITLE='�f�U�C��'>
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
<div class="title B$param{'cid'}"><B class=title>$title</B> �y$date�z�y�Q���l���F$param{'pltotal'}�l�z�y���O�C�����F��$param{'plnow'}�l�z</div>
-HEAD-
	return $return;
}

sub footer{
	print "<hr>".&dump(\%form);
	return << "-FOOT-";
<HR><div class=footlink><a href='$cgi'>$title ������ʂ�</a></div>
<HR><div class=copy>���āF<A HREF='http://game1.openspc2.org/~ssdi/'>All Rights Reserved,(C)�K���i�[ & �͂�Ԃ� LIMITED 2006-2013</A></DIV>
<HR><div class=copy>�쐬�F<A HREF='http://csyuki.sakura.ne.jp/'>Darselle</A></DIV>
</BODY></HTML>
-FOOT-
}

sub error{
	print "Content-type:text/html;\n\n";
	print << "-HTML-";
<HTML><HEAD><META NAME='ROBOTS' CONTENT='NOINDEX,FOLLOW'>
<META http-equiv='content-type' content='text/html; charset=Shift_JIS'>
<TITLE>$title -Error</TITLE></HEAD>

<BODY BGCOLOR='$bgcolor'><DIV ALIGN='center'><H3>��肪�������Ă��܂��B</H3>
<div style='color:red'><B>Error:</B> <U>$_[0]</U></div><BR>
<HR><A HREF='./$cgi'>�K���i�[ ������ʂɖ߂�</A><BR>
<FONT COLOR='#888888'>���ӁF�{�^���̘A�ł̓L�����N�^�[�̏����ɂȂ���܂�</FONT>
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
	while(!mkdir($lock,755)){select(undef,undef,undef,0.2);if($retry++>5){&error('���b�N�G���[');return 1;}}
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

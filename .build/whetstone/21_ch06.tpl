    <section class="chapter prose" id="ch06" data-ch="06">
      <header class="ch-head">
        <div class="ch-top"><span class="ch-num">Chapter 6</span><label class="done-toggle"><input type="checkbox" data-id="ch06"><span class="box"></span>Read</label></div>
        <h3>Permissions</h3>
        <div class="ch-meta"><span>{{RT}} min read</span><span>{{EX}} exercises</span></div>
        <p class="thesis">Every file has an owner, a group, and nine permission bits: read, write and execute, for the owner, for the group, and for everyone else. On a file the bits mean what they say. On a folder they mean something different, and that's where the surprises live: deleting a file needs permission on its folder, not on the file itself. This chapter decodes the bits, tries what each one allows, and covers the commands that change them, the default that sets them, and the account that ignores them.</p>
      </header>

      <h4>An owner, a group and nine bits</h4>
      <p><code>ls -l</code> starts each line with ten characters, such as <code>-rwxr-x---</code>. The first is the type: <code>-</code> for a file, <code>d</code> for a folder, <code>l</code> for a symbolic link. The other nine are three groups of three, <code>r</code> for read, <code>w</code> for write and <code>x</code> for execute, with <code>-</code> for a missing permission. The first group applies to the file's <b>owner</b>, the second to members of its <b>group</b>, and the third to everyone else, called <b>others</b>. <code>ls -l</code> also shows the owner's and group's names, and <code>id</code> shows who you are and which groups you're in.</p>
      <p>Each group of three is also a number from 0 to 7, adding 4 for <code>r</code>, 2 for <code>w</code> and 1 for <code>x</code>, so the whole mode is three digits: <code>rwxr-x---</code> is 750. You'll meet a few constantly: 644 for ordinary files, 755 for programs and folders, 600 for private files and 700 for private folders. Exactly one group applies to you, checked in order: the owner's if you own the file, otherwise the group's if you're in its group, otherwise others'. So an owner with fewer rights than the group gets the owner's rights.</p>
      <figure class="diagram">
        <svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="The mode string -rwxr-x--- split into its parts: the type, a dash for a plain file; the owner's rwx, worth 4 plus 2 plus 1, 7; the group's r-x, 4 plus 1, 5; and others' three dashes, 0; so the mode is 750. Below, what each bit allows. On a file, r lets you read its contents, w lets you change its contents, and x lets you run it as a program. On a folder, r lets you list the names in it, w lets you create, delete and rename entries in it, and x lets you go into it and reach the files inside by name.">
          __SVG:fig06__
        </svg>
        <figcaption>Ten characters, one number. The same three letters mean different things on folders, and folder permissions decide who can delete a file.</figcaption>
      </figure>

      <h4>Changing them, and the default</h4>
      <p><code>chmod</code> changes the bits, either with a number, <code>chmod 640 plan.txt</code>, or symbolically: <code>u</code>, <code>g</code>, <code>o</code> and <code>a</code> for user, group, others and all, then <code>+</code>, <code>-</code> or <code>=</code>, then the letters. So <code>chmod u+x</code> makes a file executable for its owner, and <code>chmod go-r</code> stops anyone else reading it. <code>-R</code> applies a change to a whole tree, and a capital <code>X</code> adds execute only to folders and to files that were already executable, which is usually what you want. <code>chown</code> changes the owner, which only the administrator can do, and <code>chgrp</code> the group.</p>
      <p>New files get their bits from the <b>umask</b>, a mask of permissions to remove from everything a program creates. Programs ask for 666 for files and 777 for folders, and the umask takes bits away. The usual umask, 022, removes write for the group and others, giving 644 and 755. A umask of 077 makes everything private, 600 and 700, which section 2 of the example shows. <code>umask</code> with no argument prints yours; set it in your shell's startup file, as chapter 8 does, to change it everywhere.</p>
      <p>The example sets bits with <code>chmod</code> and <code>umask</code> and reads them back, then tries real operations as an ordinary user and reports only whether each was allowed. The exact wording of "Permission denied" differs between systems, but the decisions don't.</p>
      __EXAMPLE:ch06_perms|perms.py &middot; modes decoded, chmod and umask, then reading, writing and running files, and listing, entering and deleting in folders, with the bits taken away one at a time__

      <h4>What the example shows</h4>
      <p><b>On a file, the bits mean what they say.</b> With mode <code>--w-------</code>, the owner couldn't read <code>secret.txt</code>; with <code>r--r--r--</code>, appending to <code>fixed.txt</code> was refused. <code>./hello.sh</code> failed with status 126, chapter 2's "found but not executable", while <code>bash hello.sh</code> ran it, because then <code>bash</code> is the program and only needs to read the file. Execute permission is a statement of intent, not a security barrier. Anyone who can read a script can run it.</p>
      <p><b>On a folder, they mean something else.</b> <code>r</code> lets you read the folder's list of names, so <code>echo box/*</code> worked on <code>rw-------</code>, but without <code>x</code> nothing inside could be reached: <code>cat box/note.txt</code> was refused. On a Mac, even <code>ls box</code> complains in that state, because it tries to look at each entry, which needs <code>x</code>. With <code>-wx</code>, the opposite: the names can't be listed, but a file whose name you already know can be opened. <code>w</code> on a folder means changing its list of names: without it, <code>rm box/note.txt</code> was refused even though the file itself was fine. And the last line is the surprise: a read-only file was deleted, because its folder was writable. Deleting a file removes a name from a folder, as chapter 5 explained, so it's the folder's permission that counts. Plain <code>rm</code> would have asked first, at a terminal; <code>-f</code> skipped the question, not the rule.</p>

      <h4>The administrator, and three special bits</h4>
      <p>The administrator account, <b>root</b>, user number 0, bypasses almost all of these checks, which is why the example refuses to run as root: its results would be meaningless. <code>sudo command</code> runs one command as root, after asking for your password, and records that you did. Use it for system changes, installing a package or editing a file in <code>/etc</code>, and never to make an error in your own folders go away. <code>sudo pip install</code> or <code>sudo npm install</code> leaves root-owned files in your home folder that later commands, run as you, can't change, and the fix is to correct the ownership, not to use <code>sudo</code> again.</p>
      <p>Three more bits exist. <b>Setuid</b> on a program makes it run as its owner: <code>passwd</code> is owned by root and setuid, so that you can change your own password in a file only root may write. <b>Setgid</b> on a folder, on Linux, makes new files inside it belong to the folder's group, which is how shared project folders work; macOS always does that, setgid or not. And the <b>sticky bit</b> on a folder, shown as a <code>t</code> in <code>drwxrwxrwt</code>, lets everyone create files there but each person delete only their own, which is what keeps <code>/tmp</code> civil. A Mac adds extended attributes, shown as <code>@</code> after the mode, and access control lists, shown as <code>+</code>; <code>xattr</code> and <code>ls -le</code> show them.</p>

      <div class="traps">
        <h5 class="block-h">Common traps</h5>
        <ul>
          <li><b><code>chmod -R 777</code></b> to make an error disappear, which lets every user on the machine change everything.</li>
          <li><b><code>sudo</code> on tools that write to your home folder,</b> leaving files you can no longer change.</li>
          <li><b>Forgetting <code>x</code> on a folder,</b> so readable files inside it can't be reached.</li>
          <li><b>Thinking a read-only file is safe from deletion:</b> its folder decides.</li>
          <li><b>Private keys and tokens readable by others,</b> which SSH and many other programs refuse to use.</li>
        </ul>
      </div>

      <div class="exercises">
        <h5 class="block-h">Exercises</h5>

        <div class="exercise">
          <div class="ex-head"><span class="ex-num">Exercise 6.1</span><span class="ex-title">Bits and numbers</span></div>
          <p>(a) What number is <code>rw-r-----</code>? (b) What string is 755? (c) What does <code>chmod u=rw,go=</code> leave on a file that was 755? (d) With a umask of 027, what modes do new files and folders get?</p>
          <details class="solution"><summary>Show solution</summary><div class="sol-body">
            <p>(a) 640: <code>rw-</code> is 4 + 2, <code>r--</code> is 4, <code>---</code> is 0. (b) <code>rwxr-xr-x</code>. (c) 600, <code>rw-------</code>: <code>=</code> sets a class's bits exactly, and <code>go=</code> with nothing after it removes all of them. (d) 640 for files and 750 for folders: 666 without the bits in 027 is 640, and 777 without them is 750. Running <code>umask 027; touch f; mkdir d</code> confirms it, and gives the group read access while shutting everyone else out, a common setting on shared servers. Note the umask can only remove bits: no umask makes new files executable, because programs don't ask for that bit when they create ordinary files.</p>
          </div></details>
        </div>

        <div class="exercise">
          <div class="ex-head"><span class="ex-num">Exercise 6.2</span><span class="ex-title">The key that's too open</span></div>
          <p>Running <code>ssh server</code> prints <code>WARNING: UNPROTECTED PRIVATE KEY FILE!</code> and <code>Permissions 0644 for '/home/you/.ssh/id_ed25519' are too open</code>, and then refuses to use the key. Why does SSH care, and what's the fix?</p>
          <details class="solution"><summary>Show solution</summary><div class="sol-body">
            <pre><code class="language-bash">chmod 700 ~/.ssh
chmod 600 ~/.ssh/id_ed25519          # private key: only you may read it
chmod 644 ~/.ssh/id_ed25519.pub      # public key: anyone may read it, that's its purpose</code></pre>
            <p>With 644, every user on the machine can read your private key, and anyone who has it can log in as you wherever the key is accepted. SSH refuses on principle rather than assume nobody else has an account. The fix is to remove every permission for the group and others. The folder should be 700 too, so others can't even see which keys you have. The same reasoning applies to any secret in a file, such as an API token, a <code>.env</code> file or a password store. Make them 600, and keep them out of repositories, as chapter 8 explains.</p>
          </div></details>
        </div>

        <div class="exercise">
          <div class="ex-head"><span class="ex-num">Exercise 6.3</span><span class="ex-title">A folder for a team</span></div>
          <p>On a Linux server, everyone in the group <code>web</code> should be able to create and edit files in <code>/srv/site</code>, including each other's, and nobody else should be able to change anything. Set it up.</p>
          <details class="solution"><summary>Show solution</summary><div class="sol-body">
            <pre><code class="language-bash">sudo chgrp -R web /srv/site
sudo chmod -R g+rwX,o-w /srv/site
sudo find /srv/site -type d -exec chmod g+s {} +    # new files inherit the group "web"
# and in each member's shell startup file:
umask 002                                          # new files are group-writable</code></pre>
            <p>The group gets read and write on everything, and execute on folders and on files that were already executable; that's what the capital <code>X</code> does, as running it confirms. Others lose write. Setgid on every folder makes new files belong to <code>web</code> rather than to their creator's own group, and the umask of 002 makes them group-writable when they're created, so a colleague can edit them without anyone running <code>chmod</code>. Without those two, the setup works for a day and then breaks file by file. For anything more detailed, such as one person who may read but not write, access control lists, through <code>setfacl</code>, are the next tool.</p>
          </div></details>
        </div>
      </div>

      <div class="ch-end">
        <div>
          <h5 class="block-h">Checklist</h5>
          <ul class="checklist">
            <li>Can you read a mode string, and convert between it and the octal number?</li>
            <li>Can you say what <code>r</code>, <code>w</code> and <code>x</code> allow on a file and on a folder?</li>
            <li>Can you change bits with <code>chmod</code>, both ways, and explain the umask?</li>
            <li>Can you explain who may delete a file, and why?</li>
            <li>Can you say when <code>sudo</code> is the right tool and when it makes things worse?</li>
          </ul>
        </div>
        <div>
          <h5 class="block-h">Go deeper</h5>
          <ul class="res">
            <li><span class="rkind free">Book</span><div><a href="https://linuxcommand.org/lc3_lts0090.php">Learning the Shell: Permissions</a> <span class="by">William Shotts</span></div></li>
            <li><span class="rkind free">Docs</span><div><a href="https://www.gnu.org/software/coreutils/manual/html_node/File-permissions.html">GNU Coreutils: File permissions</a> <span class="by">GNU</span></div></li>
            <li><span class="rkind free">Docs</span><div><a href="https://wiki.archlinux.org/title/File_permissions_and_attributes">File permissions and attributes</a> <span class="by">ArchWiki</span></div></li>
          </ul>
        </div>
      </div>
    </section>

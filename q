[4mGIT-ADD[24m(1)                             Git Manual                             [4mGIT-ADD[24m(1)

[1mNAME[0m
       git-add - Add file contents to the index

[1mSYNOPSIS[0m
       [1mgit add [22m[[1m--verbose [22m| [1m-v[22m] [[1m--dry-run [22m| [1m-n[22m] [[1m--force [22m| [1m-f[22m] [[1m--interactive [22m| [1m-i[22m] [[1m--patch [22m| [1m-p[22m]
               [[1m--edit [22m| [1m-e[22m] [[1m--[22m[[1mno-[22m][1mall [22m| [1m-A [22m| [1m--[22m[[1mno-[22m][1mignore-removal [22m| [[1m--update [22m| [1m-u[22m]] [[1m--sparse[22m]
               [[1m--intent-to-add [22m| [1m-N[22m] [[1m--refresh[22m] [[1m--ignore-errors[22m] [[1m--ignore-missing[22m] [[1m--renormalize[22m]
               [[1m--chmod=[22m([1m+[22m|[1m-[22m)[1mx[22m] [[1m--pathspec-from-file=[4m[22m<file>[24m [[1m--pathspec-file-nul[22m]]
               [[1m--[22m] [[4m<pathspec>[24m...]

[1mDESCRIPTION[0m
       Add contents of new or changed files to the index. The "index" (also known as the
       "staging area") is what you use to prepare the contents of the next commit.

       When you run [1mgit commit [22mwithout any other arguments, it will only commit staged
       changes. For example, if you’ve edited [1mfile.c [22mand want to commit your changes to
       that file, you can run:

           git add file.c
           git commit

       You can also add only part of your changes to a file with [1mgit add -p[22m.

       This command can be performed multiple times before a commit. It only adds the
       content of the specified file(s) at the time the add command is run; if you want
       subsequent changes included in the next commit, then you must run [1mgit add [22magain
       to add the new content to the index.

       The [1mgit status [22mcommand can be used to obtain a summary of which files have
       changes that are staged for the next commit.

       The [1mgit add [22mcommand will not add ignored files by default. You can use the
       [1m--force [22moption to add ignored files. If you specify the exact filename of an
       ignored file, [1mgit add [22mwill fail with a list of ignored files. Otherwise it will
       silently ignore the file.

       Please see [1mgit-commit[22m(1) for alternative ways to add content to a commit.

[1mOPTIONS[0m
       [4m<pathspec>[24m...
           Files to add content from. Fileglobs (e.g.  [1m*.c[22m) can be given to add all
           matching files. Also a leading directory name (e.g.  [1mdir [22mto add [1mdir/file1 [22mand
           [1mdir/file2[22m) can be given to update the index to match the current state of the
           directory as a whole (e.g. specifying [1mdir [22mwill record not just a file
           [1mdir/file1 [22mmodified in the working tree, a file [1mdir/file2 [22madded to the working
           tree, but also a file [1mdir/file3 [22mremoved from the working tree). Note that
           older versions of Git used to ignore removed files; use [1m--no-all [22moption if
           you want to add modified or new files but ignore removed ones.

           For more details about the [4m<pathspec>[24m syntax, see the [4mpathspec[24m entry in
           [1mgitglossary[22m(7).

       [1m-n[22m, [1m--dry-run[0m
           Don’t actually add the file(s), just show if they exist and/or will be
           ignored.

       [1m-v[22m, [1m--verbose[0m
           Be verbose.

       [1m-f[22m, [1m--force[0m
           Allow adding otherwise ignored files.

       [1m--sparse[0m
           Allow updating index entries outside of the sparse-checkout cone. Normally,
           [1mgit add [22mrefuses to update index entries whose paths do not fit within the
           sparse-checkout cone, since those files might be removed from the working
           tree without warning. See [1mgit-sparse-checkout[22m(1) for more details.

       [1m-i[22m, [1m--interactive[0m
           Add modified contents in the working tree interactively to the index.
           Optional path arguments may be supplied to limit operation to a subset of the
           working tree. See “Interactive mode” for details.

       [1m-p[22m, [1m--patch[0m
           Interactively choose hunks of patch between the index and the work tree and
           add them to the index. This gives the user a chance to review the difference
           before adding modified contents to the index.

           This effectively runs [1madd --interactive[22m, but bypasses the initial command
           menu and directly jumps to the [1mpatch [22msubcommand. See “Interactive mode” for
           details.

       [1m-U[4m[22m<n>[24m, [1m--unified=[4m[22m<n>[0m
           Generate diffs with [4m<n>[24m lines of context. Defaults to [1mdiff.context [22mor 3 if
           the config option is unset.

       [1m--inter-hunk-context=[4m[22m<n>[0m
           Show the context between diff hunks, up to the specified [4m<number>[24m of lines,
           thereby fusing hunks that are close to each other. Defaults to
           [1mdiff.interHunkContext [22mor 0 if the config option is unset.

       [1m-e[22m, [1m--edit[0m
           Open the diff vs. the index in an editor and let the user edit it. After the
           editor was closed, adjust the hunk headers and apply the patch to the index.

           The intent of this option is to pick and choose lines of the patch to apply,
           or even to modify the contents of lines to be staged. This can be quicker and
           more flexible than using the interactive hunk selector. However, it is easy
           to confuse oneself and create a patch that does not apply to the index. See
           EDITING PATCHES below.

       [1m-u[22m, [1m--update[0m
           Update the index just where it already has an entry matching [4m<pathspec>[24m. This
           removes as well as modifies index entries to match the working tree, but adds
           no new files.

           If no [4m<pathspec>[24m is given when [1m-u [22moption is used, all tracked files in the
           entire working tree are updated (old versions of Git used to limit the update
           to the current directory and its subdirectories).

       [1m-A[22m, [1m--all[22m, [1m--no-ignore-removal[0m
           Update the index not only where the working tree has a file matching
           [4m<pathspec>[24m but also where the index already has an entry. This adds,
           modifies, and removes index entries to match the working tree.

           If no [4m<pathspec>[24m is given when [1m-A [22moption is used, all files in the entire
           working tree are updated (old versions of Git used to limit the update to the
           current directory and its subdirectories).

       [1m--no-all[22m, [1m--ignore-removal[0m
           Update the index by adding new files that are unknown to the index and files
           modified in the working tree, but ignore files that have been removed from
           the working tree. This option is a no-op when no [4m<pathspec>[24m is used.

           This option is primarily to help users who are used to older versions of Git,
           whose [1mgit add [4m[22m<pathspec>[24m... was a synonym for [1mgit add --no-all [4m[22m<pathspec>[24m...,
           i.e. ignored removed files.

       [1m-N[22m, [1m--intent-to-add[0m
           Record only the fact that the path will be added later. An entry for the path
           is placed in the index with no content. This is useful for, among other
           things, showing the unstaged content of such files with [1mgit diff [22mand
           committing them with [1mgit commit -a[22m.

       [1m--refresh[0m
           Don’t add the file(s), but only refresh their stat() information in the
           index.

       [1m--ignore-errors[0m
           If some files could not be added because of errors indexing them, do not
           abort the operation, but continue adding the others. The command shall still
           exit with non-zero status. The configuration variable [1madd.ignoreErrors [22mcan be
           set to true to make this the default behaviour.

       [1m--ignore-missing[0m
           This option can only be used together with [1m--dry-run[22m. By using this option
           the user can check if any of the given files would be ignored, no matter if
           they are already present in the work tree or not.

       [1m--no-warn-embedded-repo[0m
           By default, [1mgit add [22mwill warn when adding an embedded repository to the index
           without using [1mgit submodule add [22mto create an entry in [1m.gitmodules[22m. This
           option will suppress the warning (e.g., if you are manually performing
           operations on submodules).

       [1m--renormalize[0m
           Apply the "clean" process freshly to all tracked files to forcibly add them
           again to the index. This is useful after changing [1mcore.autocrlf [22mconfiguration
           or the [1mtext [22mattribute in order to correct files added with wrong [4mCRLF/LF[24m line
           endings. This option implies [1m-u[22m. Lone CR characters are untouched, thus while
           a [4mCRLF[24m cleans to [4mLF[24m, a [4mCRCRLF[24m sequence is only partially cleaned to [4mCRLF[24m.

       [1m--chmod=[22m([1m+[22m|[1m-[22m)[1mx[0m
           Override the executable bit of the added files. The executable bit is only
           changed in the index, the files on disk are left unchanged.

       [1m--pathspec-from-file=[4m[22m<file>[0m
           Pathspec is passed in [4m<file>[24m instead of commandline args. If [4m<file>[24m is
           exactly [1m- [22mthen standard input is used. Pathspec elements are separated by [4mLF[0m
           or [4mCR/LF[24m. Pathspec elements can be quoted as explained for the configuration
           variable [1mcore.quotePath [22m(see [1mgit-config[22m(1)). See also [1m--pathspec-file-nul [22mand
           global [1m--literal-pathspecs[22m.

       [1m--pathspec-file-nul[0m
           Only meaningful with [1m--pathspec-from-file[22m. Pathspec elements are separated
           with [4mNUL[24m character and all other characters are taken literally (including
           newlines and quotes).

       [1m--[0m
           This option can be used to separate command-line options from the list of
           files, (useful when filenames might be mistaken for command-line options).

[1mEXAMPLES[0m
       •   Adds content from all [1m*.txt [22mfiles under [1mDocumentation [22mdirectory and its
           subdirectories:

               $ git add Documentation/\*.txt

           Note that the asterisk [1m* [22mis quoted from the shell in this example; this lets
           the command include the files from subdirectories of [1mDocumentation/[0m
           directory.

       •   Considers adding content from all [1mgit-*.sh [22mscripts:

               $ git add git-*.sh

           Because this example lets the shell expand the asterisk (i.e. you are listing
           the files explicitly), it does not consider [1msubdir/git-foo.sh[22m.

[1mINTERACTIVE MODE[0m
       When the command enters the interactive mode, it shows the output of the [4mstatus[0m
       subcommand, and then goes into its interactive command loop.

       The command loop shows the list of subcommands available, and gives a prompt
       "What now> ". In general, when the prompt ends with a single [4m>[24m, you can pick only
       one of the choices given and type return, like this:

               *** Commands ***
                 1: status       2: update       3: revert       4: add untracked
                 5: patch        6: diff         7: quit         8: help
               What now> 1

       You also could say [1ms [22mor [1msta [22mor [1mstatus [22mabove as long as the choice is unique.

       The main command loop has 6 subcommands (plus help and quit).

       status
           This shows the change between [1mHEAD [22mand index (i.e. what will be committed if
           you say [1mgit commit[22m), and between index and working tree files (i.e. what you
           could stage further before [1mgit commit [22musing [1mgit add[22m) for each path. A sample
           output looks like this:

                             staged     unstaged path
                    1:       binary      nothing foo.png
                    2:     +403/-35        +1/-1 add-interactive.c

           It shows that [1mfoo.png [22mhas differences from [1mHEAD [22m(but that is binary so line
           count cannot be shown) and there is no difference between indexed copy and
           the working tree version (if the working tree version were also different,
           [4mbinary[24m would have been shown in place of [4mnothing[24m). The other file,
           [1madd-interactive.c[22m, has 403 lines added and 35 lines deleted if you commit
           what is in the index, but working tree file has further modifications (one
           addition and one deletion).

       update
           This shows the status information and issues an "Update>>" prompt. When the
           prompt ends with double [4m>>[24m, you can make more than one selection,
           concatenated with whitespace or comma. Also you can say ranges. E.g. "2-5
           7,9" to choose 2,3,4,5,7,9 from the list. If the second number in a range is
           omitted, all remaining patches are taken. E.g. "7-" to choose 7,8,9 from the
           list. You can say [4m*[24m to choose everything.

           What you chose are then highlighted with [4m*[24m, like this:

                          staged     unstaged path
                 1:       binary      nothing foo.png
               * 2:     +403/-35        +1/-1 add-interactive.c

           To remove selection, prefix the input with [1m- [22mlike this:

               Update>> -2

           After making the selection, answer with an empty line to stage the contents
           of working tree files for selected paths in the index.

       revert
           This has a very similar UI to [4mupdate[24m, and the staged information for selected
           paths are reverted to that of the HEAD version. Reverting new paths makes
           them untracked.

       add untracked
           This has a very similar UI to [4mupdate[24m and [4mrevert[24m, and lets you add untracked
           paths to the index.

       patch
           This lets you choose one path out of a [4mstatus[24m like selection. After choosing
           the path, it presents the diff between the index and the working tree file
           and asks you if you want to stage the change of each hunk. You can select one
           of the following options and type return:

               y - stage this hunk
               n - do not stage this hunk
               q - quit; do not stage this hunk or any of the remaining ones
               a - stage this hunk and all later hunks in the file
               d - do not stage this hunk or any of the later hunks in the file
               g - select a hunk to go to
               / - search for a hunk matching the given regex
               j - go to the next undecided hunk, roll over at the bottom
               J - go to the next hunk, roll over at the bottom
               k - go to the previous undecided hunk, roll over at the top
               K - go to the previous hunk, roll over at the top
               s - split the current hunk into smaller hunks
               e - manually edit the current hunk
               p - print the current hunk
               P - print the current hunk using the pager
               ? - print help

           After deciding the fate for all hunks, if there is any hunk that was chosen,
           the index is updated with the selected hunks.

           You can omit having to type return here, by setting the configuration
           variable [1minteractive.singleKey [22mto [1mtrue[22m.

       diff
           This lets you review what will be committed (i.e. between [1mHEAD [22mand index).

[1mEDITING PATCHES[0m
       Invoking [1mgit add -e [22mor selecting [1me [22mfrom the interactive hunk selector will open a
       patch in your editor; after the editor exits, the result is applied to the index.
       You are free to make arbitrary changes to the patch, but note that some changes
       may have confusing results, or even result in a patch that cannot be applied. If
       you want to abort the operation entirely (i.e., stage nothing new in the index),
       simply delete all lines of the patch. The list below describes some common things
       you may see in a patch, and which editing operations make sense on them.

       added content
           Added content is represented by lines beginning with "+". You can prevent
           staging any addition lines by deleting them.

       removed content
           Removed content is represented by lines beginning with "-". You can prevent
           staging their removal by converting the "-" to a " " (space).

       modified content
           Modified content is represented by "-" lines (removing the old content)
           followed by "+" lines (adding the replacement content). You can prevent
           staging the modification by converting "-" lines to " ", and removing "+"
           lines. Beware that modifying only half of the pair is likely to introduce
           confusing changes to the index.

       There are also more complex operations that can be performed. But beware that
       because the patch is applied only to the index and not the working tree, the
       working tree will appear to "undo" the change in the index. For example,
       introducing a new line into the index that is in neither the [1mHEAD [22mnor the working
       tree will stage the new line for commit, but the line will appear to be reverted
       in the working tree.

       Avoid using these constructs, or do so with extreme caution.

       removing untouched content
           Content which does not differ between the index and working tree may be shown
           on context lines, beginning with a " " (space). You can stage context lines
           for removal by converting the space to a "-". The resulting working tree file
           will appear to re-add the content.

       modifying existing content
           One can also modify context lines by staging them for removal (by converting
           " " to "-") and adding a "+" line with the new content. Similarly, one can
           modify "+" lines for existing additions or modifications. In all cases, the
           new modification will appear reverted in the working tree.

       new content
           You may also add new content that does not exist in the patch; simply add new
           lines, each starting with "+". The addition will appear reverted in the
           working tree.

       There are also several operations which should be avoided entirely, as they will
       make the patch impossible to apply:

       •   adding context (" ") or removal ("-") lines

       •   deleting context or removal lines

       •   modifying the contents of context or removal lines

[1mCONFIGURATION[0m
       Everything below this line in this section is selectively included from the [1mgit-[0m
       [1mconfig[22m(1) documentation. The content is the same as what’s found there:

       [1madd.ignoreErrors[22m, [1madd.ignore-errors [22m(deprecated)
           Tells [1mgit add [22mto continue adding files when some files cannot be added due to
           indexing errors. Equivalent to the [1m--ignore-errors [22moption.  [1madd.ignore-errors[0m
           is deprecated, as it does not follow the usual naming convention for
           configuration variables.

[1mSEE ALSO[0m
       [1mgit-status[22m(1) [1mgit-rm[22m(1) [1mgit-reset[22m(1) [1mgit-mv[22m(1) [1mgit-commit[22m(1) [1mgit-update-index[22m(1)

[1mGIT[0m
       Part of the [1mgit[22m(1) suite

Git 2.52.0                             11/18/2025                             [4mGIT-ADD[24m(1)

# Adapted from http://rubayeet.wordpress.com/2012/03/26/tab-completion-for-fabric-tasks-on-os-x/
_fab_complete()
{
    local cur commands
    
    cur="${COMP_WORDS[COMP_CWORD]}"
    
    commands=$(fab -F short -l)
    
    COMPREPLY=( $(compgen -W "${commands}" -- ${cur}) )
 
    return 0
 
}
complete -o nospace -F _fab_complete fab


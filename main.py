import math

from classes import *
from os import listdir
from os.path import isfile, join



'''
Tile and gfxs
'''

## split a string separating numbers from letters
def splitStringIntoLettersAndNumbers(string):
    split_string = []
    sub_string = ""
    index = 0

    ''' TODO: REFACTOR? '''
    while index < len(string):
        if string[index].isalpha():
            while index < len(string) and string[index].isalpha():
                sub_string += string[index]
                index += 1
        elif string[index].isdigit():
             while index < len(string) and string[index].isdigit():
                sub_string += string[index]
                index += 1
        else:
            index += 1
        split_string.append(sub_string)
        sub_string = ""

    return split_string

## crop a set of tiles, getting the block in index X
def cropBlockFromGraphic(image, index, size_x, size_y, num_of_blocks=1):
    x_index = index % num_of_blocks
    x_index_pixel = x_index * size_x

    #select the tile to crop (y is always 0)
    rectangle = (x_index_pixel, 0, size_x, size_y)
    size_of_rectangle = (size_x * TILE_SCALE_FACTOR, size_y * TILE_SCALE_FACTOR)
    cropped_tile = pygame.transform.scale(image.subsurface(rectangle), size_of_rectangle)
    return cropped_tile

## get name and size properties from filename
def graphicPropertiesFromFilename(filename):
    split_filename = splitStringIntoLettersAndNumbers(filename)

    name = split_filename[0]
    height = int(split_filename[3])
    width = int(split_filename[1])

    return (name, height, width)

''' TODO: UNIFY THIS FUNCTION WITH load_ui_tiles '''
## returns dictionary
def load_game_tiles():
    game_tiles = [file for file in listdir("tiles/game/") if isfile(join("tiles/game/", file))] #load all the image files within the directory
    ui_tiles = [file for file in listdir("tiles/ui/") if isfile(join("tiles/ui/", file))]

    game_tile_dict = {} #init dictionary
    ui_tile_dict = {}
    
    #save game tiles
    for savedfile in game_tiles:
        image = pygame.image.load("tiles/game/" + savedfile).convert_alpha()

        tile_name, tile_height, tile_width = graphicPropertiesFromFilename(savedfile)

        game_tile_dict[tile_name] = (image, tile_height, tile_width)

    #save ui tiles
    for savedfile in ui_tiles:
        image = pygame.image.load("tiles/ui/" + savedfile).convert_alpha()

        tile_name, tile_height, tile_width = graphicPropertiesFromFilename(savedfile)

        ui_tile_dict[tile_name] = (image, tile_height, tile_width)        
        
    return game_tile_dict, ui_tile_dict

'''
Interpic
'''

def showTitleScreen(screen, tileset, ui_tiles):
    started_game = False
    titlepic_level = Map(1)
    clock = pygame.time.Clock()
    dave_logo = AnimatedTile("davelogo", 0)
    overlay = Scenery("blacktile", 0)
    
    #clear screen on entering
    screen.clearScreen()
    
    #init font
    davefont = pygame.font.SysFont(GAME_FONT, GAME_FONT_SIZE)
    creator_text = davefont.render("MADE BY ARTHUR, CATTANI AND MURILO", 1, (255, 255, 255))
    creator_text_width = creator_text.get_rect().width
    instr1_text = davefont.render("PRESS SPACE TO START", 1, (255, 255, 255))
    instr1_text_width = instr1_text.get_rect().width
    instr2_text = davefont.render("PRESSING ESC AT ANY MOMENT EXITS", 1, (255, 255, 255))
    instr2_text_width = instr2_text.get_rect().width
    
    while not started_game:
        pygame.display.update()
        
        screen.setXPosition(14, titlepic_level.getWidth())
        screen.printMap(titlepic_level, tileset)
        screen.printTitlepicBorder(tileset)
        screen.printTile(104, 0, dave_logo.getGraphic(ui_tiles), False)   
        screen.printTile(0, BOTTOM_OVERLAY_POS, overlay.getGraphic(ui_tiles), False)
        
        screen.printText(creator_text, screen.getUnscaledWidth()/2 - creator_text_width/(2*TILE_SCALE_FACTOR), 47)
        screen.printText(instr1_text, screen.getUnscaledWidth()/2 - instr1_text_width/(2*TILE_SCALE_FACTOR), BOTTOM_OVERLAY_POS)
        screen.printText(instr2_text, screen.getUnscaledWidth()/2 - instr2_text_width/(2*TILE_SCALE_FACTOR), BOTTOM_OVERLAY_POS+12)
        
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                started_game = True  
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return 0

        pygame.display.flip()
        clock.tick(200)
        
    #clear screen on exiting
    screen.clearScreen()
        
    return 1

def showInterpic(completed_levels, screen, GamePlayer, tileset, ui_tileset):
    Interpic = Map("interpic")

    clock = pygame.time.Clock()

    screen.setXPosition(0, Interpic.getWidth())    
    screen.printMap(Interpic, tileset)
    screen.clearBottomUi(ui_tileset)
    top_overlay = Scenery("topoverlay", 0)
    bottom_overlay = Scenery("bottomoverlay", 0)
    
    #init player
    (player, player_absolute_x, player_absolute_y) = Interpic.initPlayer(0, 0, 0)

    #init font
    davefont = pygame.font.SysFont(GAME_FONT, GAME_FONT_SIZE)
    intertext = davefont.render("GOOD WORK! ONLY " + str(NUM_OF_LEVELS - completed_levels) + " MORE TO GO!", 1, (255, 255, 255))
    intertext_width = intertext.get_rect().width
    last_level_text = davefont.render("THIS IS THE LAST LEVEL", 1, (255, 255, 255))
    last_level_text_width = last_level_text.get_rect().width
    
    player.setCurrentState(STATE.WALK)
    player.setSpriteDirection(DIRECTION.RIGHT)

    #keep moving the player right, until it reaches the screen boundary
    player_reached_boundary = (player_absolute_x >= screen.getUnscaledWidth())

    while not player_reached_boundary:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return True
                
        player_absolute_x = player.movePlayerRight(player_absolute_x)

        #print map
        screen.printMap(Interpic, tileset)
        #print text
        screen.printUi(ui_tileset, GamePlayer, completed_levels-1)
        #print text
        if completed_levels == NUM_OF_LEVELS-1:
            screen.printText(last_level_text, screen.getUnscaledWidth()/2 - last_level_text_width/(2*TILE_SCALE_FACTOR), 50)
        else:
            screen.printText(intertext, screen.getUnscaledWidth()/2 - intertext_width/(2*TILE_SCALE_FACTOR), 50)
        #print overlays
        screen.printOverlays(top_overlay, bottom_overlay, ui_tileset)
        #print player
        screen.printPlayer(player, player_absolute_x, player_absolute_y, tileset)

        player_reached_boundary = (player_absolute_x >= screen.getUnscaledWidth())

        player.updateAnimator()
        pygame.display.flip()
        clock.tick(200)
        
    return False

def showScores(screen, tileset):
    pass
    
def savePlayerScore(player_score, screen, tileset):
    pass
        
def showCreditsScreen(screen, tileset):
    pass
        
'''
Main
'''

def main():
    ##Init pygame
    pygame.init()
    game_screen = Screen(SCREEN_WIDTH, SCREEN_HEIGHT)
    
    ##Init tiles
    tileset, ui_tileset = load_game_tiles()
    top_overlay = Scenery("topoverlay", 0)
    bottom_overlay = Scenery("bottomoverlay", 0)
    
    game_open = True
    
    while game_open:
        ##Show title screen
        option = showTitleScreen(game_screen, tileset, ui_tileset)
      
        #if player presses escape, close game
        if option == 0:
            break;
      
        ##Init game
        ended_game = False
        
        ##Init a player so we can get initial scores and lives
        ''' TODO: REFACTOR THIS ? '''
        GamePlayer = Player()
      
        ##Init level and spawner
        current_level_number = 1
        current_spawner_id = 0

        ##Available Keys
        movement_keys = [pygame.K_UP, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_DOWN]
        inv_keys = [pygame.K_LCTRL, pygame.K_RCTRL, pygame.K_LALT, pygame.K_RALT]

        ##Game processing
        while not ended_game:
            # init clock and display
            clock = pygame.time.Clock()
            pygame.display.update()

            # build the level and init screen and player positions
            Level = Map(current_level_number)
            (GamePlayer, player_position_x, player_position_y) = Level.initPlayer(current_spawner_id, GamePlayer.getScore(), GamePlayer.getLives())
            game_screen.setXPosition(Level.getPlayerSpawnerPosition(current_spawner_id)[0] - 10, Level.getWidth())
            
            # init other sprites
            death_timer = -1
            friendly_shot = 0

            # UI Inits
            score_ui = 0 #initial score, everytime it changes, we update the ui
            jetpack_ui = False 

            # level processing controller
            ended_level = False

            ## Level processing
            while not ended_level:
            
                # get keys (inventory)
                for event in pygame.event.get():
                    if event.type == pygame.KEYUP:
                        if event.key in [pygame.K_LEFT, pygame.K_RIGHT] and GamePlayer.getCurrentState() in [STATE.WALK, STATE.FLY, STATE.JUMP, STATE.CLIMB]:
                            GamePlayer.clearXMovement()
                        elif event.key in [pygame.K_UP, pygame.K_DOWN] and GamePlayer.getCurrentState() in [STATE.FLY, STATE.CLIMB]:
                            GamePlayer.setVelocityY(0)
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            game_open = False
                            ended_level = True
                            ended_game = True
                        elif event.key in inv_keys:
                            if GamePlayer.inventoryInput(inv_keys.index(event.key)) and not friendly_shot:
                                friendly_shot = Level.spawnFriendlyFire(GamePlayer.getSpriteDirection())
                                friendly_shot_x, friendly_shot_y = player_position_x + GamePlayer.getDirectionX().value * WIDTH_OF_MAP_NODE, player_position_y

                # get keys (movement)
                pressed_keys = pygame.key.get_pressed()
                key_map = [0,0,0,0]
                for i, key in enumerate(movement_keys):
                    if pressed_keys[key]:
                        key_map[i] = 1
                GamePlayer.movementInput(key_map)

                # update the player position in the level and treat collisions
                if GamePlayer.getCurrentState() != STATE.DESTROY:
                    (player_position_x, player_position_y) = GamePlayer.updatePosition(player_position_x, player_position_y, Level)
                    
                # if the player is out of the screen bottom boundary (fell), send him to the top
                if player_position_y >= game_screen.getUnscaledHeight():
                    player_position_y = 0
                    
                # update friendly shot position, if there is one
                if friendly_shot:
                    friendly_shot_x = friendly_shot.updatePosition(friendly_shot_x, friendly_shot_y, Level)
                    if (friendly_shot_x == -1):
                        del friendly_shot
                        friendly_shot = 0

                # if the player ended the level, go on to the next
                if GamePlayer.getCurrentState() == STATE.ENDMAP:
                    ended_level = True
                    break;
                # if the player died, spawn death puff and respawn player (if he has enough lives)
                elif GamePlayer.getCurrentState() == STATE.DESTROY:
                    ''' TODO: REFACTOR '''
                    if death_timer == -1:
                        GamePlayer.takeLife()
                        DeathPuff = AnimatedTile("explosion", 0)
                        death_timer = 120
                    
                    player_position_y += 0.25
                    death_timer -= 1
                    
                    if death_timer == 0:
                        death_timer = -1
                        game_screen.setXPosition(Level.getPlayerSpawnerPosition(current_spawner_id)[0] - 10, Level.getWidth())
                        del DeathPuff
                        
                        if (GamePlayer.resetPosAndState() != -1):
                            (player_position_x, player_position_y) = Level.getPlayerSpawnerPosition(current_spawner_id)
                            player_position_x *= WIDTH_OF_MAP_NODE
                            player_position_y *= HEIGHT_OF_MAP_NODE
                        else:
                            ended_level = True
                            ended_game = True
                    
                # if the player is close enough to one of the screen boundaries, move the screen.
                player_close_to_left_boundary = (player_position_x <= game_screen.getXPositionInPixelsUnscaled() + BOUNDARY_DISTANCE_TRIGGER)
                player_close_to_right_boundary = (player_position_x >= game_screen.getXPositionInPixelsUnscaled() + game_screen.getUnscaledWidth() - BOUNDARY_DISTANCE_TRIGGER)
                reached_level_left_boundary = (game_screen.getXPosition() <= 0)
                reached_level_right_boundary = (game_screen.getXPosition() + game_screen.getWidthInTiles() > Level.getWidth())         

                # move screen left
                if player_close_to_left_boundary and not reached_level_left_boundary:
                    game_screen.moveScreenX(Level, -15, tileset, top_overlay, bottom_overlay, ui_tileset)
                # move screen right
                elif player_close_to_right_boundary and not reached_level_right_boundary:
                    game_screen.moveScreenX(Level, 15, tileset, top_overlay, bottom_overlay, ui_tileset)
                # not moving (just update the screen)
                else:
                    game_screen.printMap(Level, tileset)
                    
                    if friendly_shot:
                        game_screen.printTile(friendly_shot_x - game_screen.getXPositionInPixelsUnscaled(), friendly_shot_y, friendly_shot.getGraphic(tileset))
                        
                        bullet_bypassed_screen_right_boundary = (friendly_shot_x >= game_screen.getXPositionInPixelsUnscaled() + game_screen.getUnscaledWidth())
                        bullet_bypassed_screen_left_boundary = (friendly_shot_x <= game_screen.getXPositionInPixelsUnscaled())
                        
                        if bullet_bypassed_screen_right_boundary or bullet_bypassed_screen_left_boundary:
                            del friendly_shot
                            friendly_shot = 0
                    
                    if GamePlayer.getCurrentState() != STATE.DESTROY:
                        # print player accordingly to screen shift
                        game_screen.printPlayer(GamePlayer, player_position_x - game_screen.getXPositionInPixelsUnscaled(), player_position_y, tileset)
                    elif not ended_game:
                        # print death puff accordingly to screen shift
                        game_screen.printTile(player_position_x - game_screen.getXPositionInPixelsUnscaled(), player_position_y, DeathPuff.getGraphic(tileset))

                # update UI
                game_screen.printOverlays(top_overlay, bottom_overlay, ui_tileset)
                game_screen.printUi(ui_tileset, GamePlayer, current_level_number)
                
                if not ended_level:
                    if GamePlayer.inventory["gun"] == 1:
                        updateUiGun(ui_tileset)
                    if GamePlayer.inventory["jetpack"] == 1 or jetpack_ui :
                        game_screen.updateUiJetpack(ui_tileset, GamePlayer.inventory["jetpack"])
                        jetpack_ui = True
                    if GamePlayer.inventory["trophy"] == 1:
                        game_screen.updateUiTrophy(ui_tileset)
                        
                
                if score_ui != GamePlayer.score:
                    game_screen.updateUiScore(ui_tileset,GamePlayer.score)
                    score_ui = GamePlayer.score                
                    
                pygame.display.flip()
                pygame.event.pump() 
                clock.tick(200)

            # Onto the next level
            current_level_number += 1
            current_spawner_id = 0
            
            if current_level_number > NUM_OF_LEVELS and ended_level and not ended_game:
                showCreditsScreen(game_screen, tileset)
                ended_game = True
            elif ended_level and not ended_game:
                option = showInterpic(current_level_number, game_screen, GamePlayer, tileset, ui_tileset)
                ended_game = option
                game_open = not option
                
        savePlayerScore(GamePlayer.getScore(), game_screen, tileset)
        showScores(game_screen, tileset)
                
    pygame.quit()
    quit()

if __name__ == "__main__":
    main()
